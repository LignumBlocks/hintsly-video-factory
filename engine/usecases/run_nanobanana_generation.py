from typing import List, Dict
from domain.nanobanana_models import NanoBananaRequest, NanoBananaImageTask
from adapters.nanobanana_repository import NanoBananaRepository
from adapters.nanobanana_client import NanoBananaClient
from adapters.assets_repository import AssetsRepository
from usecases.nanobanana_prompt_service import NanoBananaPromptService
from adapters.logger import Logger
from infra.config import Config
import os

class RunNanoBananaGeneration:
    def __init__(self, 
                 repository: NanoBananaRepository, 
                 prompt_service: NanoBananaPromptService,
                 client: NanoBananaClient,
                 assets_repository: AssetsRepository,
                 logger: Logger):
        self.repository = repository
        self.prompt_service = prompt_service
        self.client = client
        self.assets_repository = assets_repository
        self.logger = logger
        self.public_base_url = Config.PUBLIC_BASE_URL

    def execute(self, project_id: str, dry_run: bool = False):
        from infra.paths import ASSETS_DIR
        request: NanoBananaRequest = self.repository.get(project_id)
        if not request:
            raise ValueError(f"Project {project_id} not found in repository.")

        tasks = request.image_tasks
        self.logger.info(f"Starting generation for project {project_id}. Total tasks: {len(tasks)}")

        all_results = []

        for task in tasks:
            try:
                # 1. Construct Prompts
                prompt = self.prompt_service.construct_prompt(request.style_presets, task)
                neg_prompt = self.prompt_service.construct_negative_prompt(request.style_presets, task)

                # 2. Resolve Refs to URLs (with IDs for UI)
                assets_sent = self._resolve_refs_detailed(task.refs)
                ref_urls = [a["resolved_url"] for a in assets_sent]

                # 3. Call API
                self.logger.info(f"Generating Task {task.task_id}...")
                
                if dry_run:
                    self.logger.info("[DRY RUN] Skipping API call.")
                    generated_urls = ["http://mock.url/img1.png"]
                else:
                    generated_urls = self.client.generate_image(
                        prompt=prompt,
                        negative_prompt=neg_prompt,
                        reference_images=ref_urls,
                        resolution=request.project.output.resolution_px,
                        num_outputs=request.project.production_rules.nanobanana_variants_per_image_task,
                        output_format=request.project.output.image_format
                    )
                
                # 4. DOWNLOAD & PERSIST
                self.logger.info(f"Generated {len(generated_urls)} images. Downloading...")
                
                # Set output dir: assets/videos/{project_id}/{task_id}/{block_id}/{shot_id}
                base_output_dir = os.path.join(str(ASSETS_DIR), "videos", project_id, task.task_id, task.block_id, task.shot_id)
                os.makedirs(base_output_dir, exist_ok=True)
                
                import httpx
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                for i, url in enumerate(generated_urls):
                    try:
                        variant_index = i + 1
                        # Filename: img_{role}.{ext} (handling variants if needed)
                        variant_suffix = f"_v{variant_index}" if len(generated_urls) > 1 else ""
                        filename = f"img_{task.role}{variant_suffix}.png" 
                        filepath = os.path.join(base_output_dir, filename)

                        public_url = url # Default to temp URL from API
                        if not dry_run:
                            resp = httpx.get(url, timeout=30)
                            if resp.status_code == 200:
                                with open(filepath, "wb") as f:
                                    f.write(resp.content)
                                
                                # Resolve local path to public URL
                                rel_path = os.path.relpath(filepath, start=str(ASSETS_DIR))
                                rel_path_url = rel_path.replace('\\', '/')
                                public_url = f"{self.public_base_url}/assets/{rel_path_url}"
                                self.logger.info(f"Saved locally: {public_url}")
                            else:
                                self.logger.error(f"Failed to download {url}: {resp.status_code}")
                        else:
                            self.logger.info(f"[DRY RUN] Would download {url} to {filepath}")

                        all_results.append({
                            "task_id": task.task_id,
                            "variant": variant_index,
                            "image_url": public_url,
                            "final_prompt": prompt,
                            "final_negative_prompt": neg_prompt,
                            "assets_sent": assets_sent
                        })
                    except Exception as download_err:
                        self.logger.error(f"Download exception for {url}: {download_err}")

                # Ticket IMG-08: Approval Gate
                task.approval.status = "PENDING_REVIEW"
                self.repository.save(request)
                
            except Exception as e:
                self.logger.error(f"Task {task.task_id} failed: {e}")
                # We don't append a failed result here to avoid breaking the UI list, 
                # or we could append it with status: "ERROR" if the contract allowed.
                # For now, let the caller handle exceptions.

        return all_results
    
    def check_project_approval(self, project_id: str) -> bool:
        """
        Ticket IMG-08: Approval Gate Logic.
        Returns True if the project is allowed to proceed (e.g. to video generation).
        Returns False if there are unapproved tasks when the gate is active.
        """
        request: NanoBananaRequest = self.repository.get(project_id)
        if not request:
            return False # Fail safe
            
        gate_active = request.project.production_rules.approval_gate != "none" # Assuming it might be a string rule description or bool? 
        # Checking models.py to see type of approval_gate. It seems to be a description string in the JSON example.
        # "approval_gate": "REQUIRED: All image outputs must be approved..."
        # If we treat any non-empty / non-false string as active.
        
        # Let's check models.py type.
        # NanoBananaProductionRules.approval_gate is str. 
        # If it says "REQUIRED...", we treat it as True. 
        # If it was "false" or empty, maybe False. 
        # Let's assume strict check: if not empty string -> Gate Active.
        
        if not gate_active:
             return True
             
        pending_tasks = [t.task_id for t in request.image_tasks if t.approval.status != "APPROVED"]
        
        if pending_tasks:
            self.logger.info(f"Project {project_id} blocked by approval gate. Pending tasks: {len(pending_tasks)}")
            return False
            
        self.logger.info(f"Project {project_id} approved to proceed.")
        return True

    def _resolve_refs_detailed(self, refs: List[str]) -> List[Dict[str, str]]:
        from infra.paths import ASSETS_DIR
        detailed_refs = []
        for ref_id in refs:
            asset = self.assets_repository.get_asset(ref_id)
            if asset:
                 path = self.assets_repository.resolve_file_path(asset.file_name)
                 if path:
                     try:
                         rel_path = os.path.relpath(path, start=str(ASSETS_DIR))
                         rel_path_url = rel_path.replace('\\', '/')
                         url = f"{self.public_base_url}/assets/{rel_path_url}"
                         detailed_refs.append({
                             "ref_id": ref_id,
                             "resolved_url": url
                         })
                     except ValueError:
                        self.logger.warning(f"Asset path {path} is not inside ASSETS_DIR {ASSETS_DIR}")
        return detailed_refs

    def _resolve_refs_to_urls(self, refs: List[str]) -> List[str]:
        return [a["resolved_url"] for a in self._resolve_refs_detailed(refs)]
