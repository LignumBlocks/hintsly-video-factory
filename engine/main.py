from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import Optional, List, Dict
import traceback

from domain.entities import Shot, ShotEstado
from usecases.process_shot import ProcessShot
from usecases.regenerate_shot import RegenerateShot
from usecases.utils_prompt import PromptService
from usecases.ingest_nanobanana import IngestNanoBanana
from usecases.run_nanobanana_generation import RunNanoBananaGeneration
from usecases.nanobanana_prompt_service import NanoBananaPromptService
from domain.nanobanana_models import NanoBananaRequest
from adapters.fs_adapter import FSAdapter
from adapters.gemini_client import GeminiImageClient
from adapters.veo_client import VeoClient
from adapters.nanobanana_client import NanoBananaClient
from adapters.logger import Logger
from infra.paths import ASSETS_DIR
from adapters.assets_repository import AssetsRepository
from adapters.nanobanana_repository import NanoBananaRepository
from infra.config import Config

# Initialize FastAPI app
app = FastAPI(
    title="Hintsly Video Factory API",
    description="API for generating AI-powered video shots with image-to-video pipeline",
    version="1.0.0"
)

from fastapi.exceptions import RequestValidationError

# CORS middleware for n8n integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation Error: {exc.errors()}")
    logger.error(f"Body: {await request.body()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": str(await request.body())},
    )

# Mount static files to serve images publicly
# This allows Kie.ai Veo to access images via URL
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Instantiate adapters
fs_adapter = FSAdapter()
prompt_service = PromptService()
gemini_client = GeminiImageClient()
veo_client = VeoClient()

logger = Logger()
assets_repository = AssetsRepository(files_dir=Config.ASSETS_FILES_DIR)
nanobanana_repository = NanoBananaRepository()
nanobanana_client = NanoBananaClient()
prompt_service = NanoBananaPromptService()

# Instantiate use cases
process_shot_usecase = ProcessShot(
    fs_adapter, 
    prompt_service, 
    gemini_client, 
    veo_client, 
    logger,
    assets_repository
)
regenerate_shot_usecase = RegenerateShot(process_shot_usecase)
ingest_nanobanana_usecase = IngestNanoBanana(nanobanana_repository, assets_repository, logger)
run_nanobanana_generation_usecase = RunNanoBananaGeneration(nanobanana_repository, prompt_service, nanobanana_client, assets_repository, logger)



# Response Models
class ShotProcessResponse(BaseModel):
    """Structured response for shot processing"""
    success: bool
    shot: Shot
    message: str
    
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    public_base_url: str

class IngestResponse(BaseModel):
    """Response for NanoBanana ingestion"""
    success: bool
    project_id: str
    message: str


@app.get("/health", response_model=HealthResponse)
def health_check():
    """
    Health check endpoint for monitoring and n8n integration validation.
    """
    return HealthResponse(
        status="healthy",
        service="hintsly-video-factory",
        version="1.0.0",
        public_base_url=Config.PUBLIC_BASE_URL
    )


@app.post("/shots/process", response_model=ShotProcessResponse)
def process_shot(shot: Shot):
    """
    Process a single shot through the complete pipeline:
    1. Resolve asset (if asset_id provided)
    2. Generate image using Nano Banana
    3. Generate video using Veo (if asset_mode requires it)
    4. Save files and metadata
    
    Args:
        shot: Shot entity with all required fields
        
    Returns:
        ShotProcessResponse with success status and updated shot data
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        logger.info(f"🎬 Processing shot: {shot.video_id}/{shot.block_id}/{shot.shot_id}")
        logger.info(f"🔍 DEBUG: Received asset_id: '{shot.asset_id}' (Type: {type(shot.asset_id)})")
        
        # Execute the use case
        result = process_shot_usecase.execute(shot)
        
        # Check if processing was successful
        if result.estado == ShotEstado.COMPLETADO:
            logger.info(f"✅ Shot processed successfully: {result.shot_id}")
            
            # MODIFY RESPONSE: Replace local paths with public URLs for client convenience
            # This does not affect the metadata saved on disk (which keeps local paths)
            if result.image_path:
                result.image_path = fs_adapter.get_public_url(result.image_path)
            if result.video_path:
                result.video_path = fs_adapter.get_public_url(result.video_path)
            
            return ShotProcessResponse(
                success=True,
                shot=result,
                message=f"Shot {result.shot_id} processed successfully"
            )
        else:
            logger.error(f"❌ Shot processing failed: {result.error_message}")
            return ShotProcessResponse(
                success=False,
                shot=result,
                message=f"Shot processing failed: {result.error_message}"
            )
            
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid shot data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error processing shot: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/shots/regenerate", response_model=ShotProcessResponse)
def regenerate_shot(shot: Shot):
    """
    Regenerate a shot (useful for retrying failed shots or updating existing ones).
    
    Args:
        shot: Shot entity with existing data
        
    Returns:
        ShotProcessResponse with success status and updated shot data
    """
    try:
        logger.info(f"🔄 Regenerating shot: {shot.video_id}/{shot.block_id}/{shot.shot_id}")
        
        result = regenerate_shot_usecase.execute(shot)
        
        if result.estado == ShotEstado.COMPLETADO:
            logger.info(f"✅ Shot regenerated successfully: {result.shot_id}")
            
            # MODIFY RESPONSE: Replace local paths with public URLs
            if result.image_path:
                result.image_path = fs_adapter.get_public_url(result.image_path)
            if result.video_path:
                result.video_path = fs_adapter.get_public_url(result.video_path)
                
            return ShotProcessResponse(
                success=True,
                shot=result,
                message=f"Shot {result.shot_id} regenerated successfully"
            )
        else:
            logger.error(f"❌ Shot regeneration failed: {result.error_message}")
            return ShotProcessResponse(
                success=False,
                shot=result,
                message=f"Shot regeneration failed: {result.error_message}"
            )
            
    except Exception as e:
        logger.error(f"Error regenerating shot: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/nanobanana/ingest", response_model=IngestResponse)
def ingest_nanobanana(request: NanoBananaRequest):
    """
    Ingest a NanoBananaPro project JSON definition.
    """
    try:
        project_id = ingest_nanobanana_usecase.execute(request)
        return IngestResponse(
            success=True,
            project_id=project_id,
            message=f"Project {project_id} ingested successfully"
        )
    except Exception as e:
        logger.error(f"Error ingesting NanoBanana project: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting project: {str(e)}"
        )

class GenerateRequest(BaseModel):
    project_id: str
    dry_run: bool = False

class GenerateResponse(BaseModel):
    job_id: Optional[str] = None
    status: str
    results: List[Dict] = []
    error: Optional[str] = None

@app.post("/nanobanana/generate", response_model=GenerateResponse)
def generate_nanobanana(req: GenerateRequest):
    """
    Trigger image generation for all pending tasks in a project.
    """
    try:
        results = run_nanobanana_generation_usecase.execute(req.project_id, dry_run=req.dry_run)
        return GenerateResponse(
            status="DONE",
            results=results
        )
    except Exception as e:
        logger.error(f"Error in NanoBanana generation: {e}")
        logger.error(traceback.format_exc())
        return GenerateResponse(
            status="ERROR",
            error=str(e)
        )

@app.post("/nanobanana/run-full", response_model=GenerateResponse)
def run_full_nanobanana(request: NanoBananaRequest):
    """
    Ingest and run generation in one call for the UI Runner.
    """
    try:
        # 1. Ingest
        project_id = ingest_nanobanana_usecase.execute(request)
        
        # 2. Run
        results = run_nanobanana_generation_usecase.execute(project_id)
        
        return GenerateResponse(
            job_id=project_id,
            status="DONE",
            results=results
        )
    except Exception as e:
        logger.error(f"Error in run-full: {e}")
        logger.error(traceback.format_exc())
        return GenerateResponse(
            status="ERROR",
            error=str(e)
        )
