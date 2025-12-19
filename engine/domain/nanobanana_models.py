from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class NanoBananaFileInfo(BaseModel):
    pipeline_context: str
    version: str
    target_tool: str

class NanoBananaOutputConfig(BaseModel):
    aspect_ratio: str
    resolution_px: List[int]
    image_format: str

class NanoBananaProductionRules(BaseModel):
    nanobanana_max_reference_images: int
    nanobanana_variants_per_image_task: int
    approval_gate: str

class NanoBananaProject(BaseModel):
    project_id: str
    title: str
    scope_blocks_included: List[str]
    output: NanoBananaOutputConfig
    production_rules: NanoBananaProductionRules

class NanoBananaStylePresets(BaseModel):
    global_image_style: str
    global_negative_append: str

class NanoBananaApproval(BaseModel):
    status: str

class NanoBananaImageTask(BaseModel):
    task_id: str
    block_id: str
    shot_id: str
    role: str
    refs: List[str]
    prompt: str
    negative_prompt: Optional[str] = None
    approval: NanoBananaApproval

class NanoBananaRequest(BaseModel):
    file_info: Optional[NanoBananaFileInfo] = None
    project: NanoBananaProject
    asset_library: Dict[str, Dict[str, str]]
    style_presets: Optional[NanoBananaStylePresets] = None
    image_tasks: List[NanoBananaImageTask]
