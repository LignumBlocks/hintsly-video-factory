from pydantic import BaseModel
from typing import Optional

class Shot(BaseModel):
    video_id: str
    bloque: str
    plano: int
    descripcion_visual: str
    movimiento_camara: str
    prompt_imagen: Optional[str] = None
    prompt_video: Optional[str] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    estado: Optional[str] = None
    error_message: Optional[str] = None
