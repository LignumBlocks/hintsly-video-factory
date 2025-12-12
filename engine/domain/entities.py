from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class AssetMode(str, Enum):
    """Asset generation mode for the shot"""
    STILL_ONLY = "STILL_ONLY"
    IMAGE_1F_VIDEO = "IMAGE_1F_VIDEO"
    IMAGE_2F_VIDEO = "IMAGE_2F_VIDEO"

class ShotEstado(str, Enum):
    """Shot processing state"""
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"

class Asset(BaseModel):
    """Asset Definition from Catalog"""
    asset_id: str
    file_name: str
    tipo_asset: str
    mv_context_default: str
    descripcion_visual: str
    uso_sugerido: str
    notas: Optional[str] = None

class Shot(BaseModel):
    """
    Shot Schema V2 (Hintsly Lab Canon)
    Represents a single shot in a video with all metadata for generation.
    """
    # Identifiers
    video_id: str
    block_id: str
    shot_id: str
    
    # Control fields
    core_flag: bool = False
    mv_context: str
    asset_id: Optional[str] = None
    asset_mode: AssetMode
    
    # Asset Resolution Metadata (New)
    asset_resolved_file_name: Optional[str] = None
    asset_resolved_path: Optional[str] = None
    asset_mv_context_mismatch: bool = False
    
    # Camera & timing
    camera_move: str
    duracion_seg: float
    
    # Semantic fields
    texto_voz_resumido: str
    descripcion_visual: str
    funcion_narrativa: str
    
    # Generated fields (populated by the pipeline)
    prompt_imagen: Optional[str] = None
    prompt_video: Optional[str] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    
    # State management
    estado: ShotEstado = ShotEstado.PENDIENTE
    error_message: Optional[str] = None

