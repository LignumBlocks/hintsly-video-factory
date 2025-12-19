from domain.nanobanana_models import NanoBananaRequest
from adapters.nanobanana_repository import NanoBananaRepository
from adapters.logger import Logger

class IngestNanoBanana:
    def __init__(self, repository: NanoBananaRepository, logger: Logger):
        self.repository = repository
        self.logger = logger

    def execute(self, request_data: NanoBananaRequest) -> str:
        self.logger.info(f"Ingesting NanoBanana project: {request_data.project.project_id}")
        
        # Validation is mostly handled by Pydantic before reaching here,
        # but we can add business logic validation here if needed.
        
        saved_id = self.repository.save(request_data)
        self.logger.info(f"Successfully ingested project {saved_id} into memory.")
        return saved_id
