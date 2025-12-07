import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger

APP_VERSION = "0.1.0"

# Rutas de assets dentro del contenedor
ASSETS_ROOT = Path(os.getenv("ASSETS_PATH", "/assets/videos")).resolve()
TMP_ROOT = ASSETS_ROOT.parent / "tmp"

# Crear las carpetas si no existen
ASSETS_ROOT.mkdir(parents=True, exist_ok=True)
TMP_ROOT.mkdir(parents=True, exist_ok=True)

logger.info(f"Using ASSETS_ROOT={ASSETS_ROOT}")
logger.info(f"Using TMP_ROOT={TMP_ROOT}")

app = FastAPI(
    title="Hintsly Video Factory Engine",
    version=APP_VERSION,
    description="Engine mínimo para orquestar planos de vídeo (versión mock).",
)


# ---- MODELOS --------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    version: str
    assets_path: str


class ShotRequest(BaseModel):
    """Payload que enviará n8n para procesar un plano."""
    id: str
    description: str
    block: Optional[str] = None  # bloque / escena opcional


class ShotResponse(BaseModel):
    id: str
    description: str
    status: str
    image_path: Optional[str] = None
    video_path: Optional[str] = None


# ---- ENDPOINTS ------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Endpoint de salud para comprobar que el contenedor responde.
    Úsalo desde n8n o curl: GET /health
    """
    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        assets_path=str(ASSETS_ROOT),
    )


@app.post("/shots/process", response_model=ShotResponse)
def process_shot(shot: ShotRequest) -> ShotResponse:
    """
    Endpoint MOCK: no genera vídeo real todavía.
    - Crea un archivo de texto en la carpeta de vídeos simulando el resultado.
    - Devuelve rutas que luego n8n puede registrar en la tabla.
    """
    logger.info(f"Received shot to process: id={shot.id} block={shot.block!r}")

    # Archivo "dummy" que representa el vídeo generado
    dummy_video_path = ASSETS_ROOT / f"{shot.id}.txt"
    dummy_video_path.write_text(
        f"Placeholder for shot {shot.id}\n"
        f"Description: {shot.description}\n"
        f"Block: {shot.block or '-'}\n"
    )

    logger.info(f"Mock video created at {dummy_video_path}")

    return ShotResponse(
        id=shot.id,
        description=shot.description,
        status="mock_generated",
        image_path=None,            # más adelante pondremos la ruta real
        video_path=str(dummy_video_path),
    )
