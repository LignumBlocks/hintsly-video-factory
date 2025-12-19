from domain.nanobanana_models import NanoBananaRequest
from adapters.nanobanana_repository import NanoBananaRepository
from adapters.assets_repository import AssetsRepository
from adapters.logger import Logger

class IngestNanoBanana:
    def __init__(self, repository: NanoBananaRepository, assets_repository: AssetsRepository, logger: Logger):
        self.repository = repository
        self.assets_repository = assets_repository
        self.logger = logger

    def execute(self, request_data: NanoBananaRequest) -> str:
        self.logger.info(f"Ingesting NanoBanana project: {request_data.project.project_id}")
        
        
        # Validation Logic
        self._validate_refs(request_data)
        
        saved_id = self.repository.save(request_data)
        self.logger.info(f"Successfully ingested project {saved_id} into memory.")
        return saved_id

    def _validate_refs(self, data: NanoBananaRequest):
        """
        Validates that all refs in image_tasks:
        1. Exist in the provided asset_library (or are known IDs).
        2. Exist in the AssetsRepository (physical check).
        3. Do not exceed the maximum allowed refs.
        """
        max_refs = data.project.production_rules.nanobanana_max_reference_images
        
        # Flatten asset_library to get a set of valid Asset IDs defined in the JSON
        # Structure: category -> (asset_key -> asset_id) OR (list of items)
        valid_json_ids = set()
        for category_name, category_content in data.asset_library.items():
            if isinstance(category_content, dict):
                for asset_id in category_content.values():
                    valid_json_ids.add(asset_id)
            elif isinstance(category_content, list):
                # Handle lists like "notes" - though usually they aren't IDs 
                # but we'll be safe and skip or include them if they look like IDs.
                pass 

        for task in data.image_tasks:
            # 1. Check Max Refs
            if len(task.refs) > max_refs:
                raise ValueError(f"Task {task.task_id} has {len(task.refs)} refs, exceeding limit of {max_refs}.")

            for ref in task.refs:
                # 2. Check existence in JSON library
                if ref not in valid_json_ids:
                    raise ValueError(f"Task {task.task_id} references unknown asset ID in JSON: '{ref}'")

                # 3. Check existence in System Repository (Physical/Catalog check)
                asset = self.assets_repository.get_asset(ref)
                if not asset:
                    # Warning or Error? Ticket says "Error claro si un asset no existe"
                    # But if we strictly enforce this, we need the assets to be in the catalog.
                    raise ValueError(f"Task {task.task_id} references asset '{ref}' not found in System Catalog.")
                
                # Check physical file existence
                # We use the file_name from the asset to resolve the path
                path = self.assets_repository.resolve_file_path(asset.file_name)
                if not path:
                     raise ValueError(f"Physical file for asset '{ref}' ({asset.file_name}) not found on disk.")
