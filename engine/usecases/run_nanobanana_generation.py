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
        request: NanoBananaRequest = self.repository.get(project_id)
        if not request:
            raise ValueError(f"Project {project_id} not found in repository.")

        tasks = request.image_tasks
        self.logger.info(f"Starting generation for project {project_id}. Total tasks: {len(tasks)}")

        results = {}

        for task in tasks:
            if task.approval.status != "PENDING_REVIEW": # Only process pending? Or maybe all? Ticket doesn't specify skipping.
                # Assuming force processing or processing all for now unless specified.
                pass
            
            try:
                # 1. Construct Prompts
                prompt = self.prompt_service.construct_prompt(request.style_presets, task)
                neg_prompt = self.prompt_service.construct_negative_prompt(request.style_presets, task)

                # 2. Resolve Refs to URLs
                ref_urls = self._resolve_refs_to_urls(task.refs)

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
                local_files = []
                self.logger.info(f"Generated {len(generated_urls)} images. Downloading...")
                
                # Setup output dir: outputs/{project_id}/{block_id}/{shot_id}/
                # Assuming simple structure based on ticket description or generic outputs/project_id first.
                # Implementation plan said: outputs/{project_id}/{block_id}/{shot_id}/{task_id}_v{i}.png
                
                base_output_dir = os.path.join("outputs", project_id, task.block_id, task.shot_id)
                os.makedirs(base_output_dir, exist_ok=True)
                
                import httpx
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                for i, url in enumerate(generated_urls):
                    try:
                        if dry_run:
                            self.logger.info(f"[DRY RUN] Would download {url}")
                            local_files.append(f"{base_output_dir}/mock_{i}.png")
                            continue
                            
                        resp = httpx.get(url, timeout=30)
                        if resp.status_code == 200:
                            # Filename: {task_id}_v{i+1}_{timestamp}.png
                            filename = f"{task.task_id}_v{i+1}_{timestamp}.png"
                            filepath = os.path.join(base_output_dir, filename)
                            
                            with open(filepath, "wb") as f:
                                f.write(resp.content)
                            
                            local_files.append(filepath)
                            self.logger.info(f"Saved: {filepath}")
                        else:
                            self.logger.error(f"Failed to download {url}: {resp.status_code}")
                    except Exception as download_err:
                        self.logger.error(f"Download exception for {url}: {download_err}")

                results[task.task_id] = local_files
                
            except Exception as e:
                self.logger.error(f"Task {task.task_id} failed: {e}")
                results[task.task_id] = {"error": str(e)}

        return results

    def _resolve_refs_to_urls(self, refs: List[str]) -> List[str]:
        from infra.paths import ASSETS_DIR
        urls = []
        for ref in refs:
            # Get Asset (this implicitly checks existence and creates if just file)
            asset = self.assets_repository.get_asset(ref)
            if asset:
                 # Resolve physical file path to ensure it exists
                 path = self.assets_repository.resolve_file_path(asset.file_name)
                 if path:
                     # Calculate relative path from ASSETS_DIR for correct URL construction
                     # e.g. path = .../assets/catalog_files/foo.png -> catalog_files/foo.png
                     try:
                        rel_path = os.path.relpath(path, start=str(ASSETS_DIR))
                        # Enforce forward slashes for URLs even on Windows (though running on Linux)
                        rel_path_url = rel_path.replace("\\", "/")
                        url = f"{self.public_base_url}/assets/{rel_path_url}"
                        urls.append(url)
                     except ValueError:
                        self.logger.warning(f"Asset path {path} is not inside ASSETS_DIR {ASSETS_DIR}")
        return urls
