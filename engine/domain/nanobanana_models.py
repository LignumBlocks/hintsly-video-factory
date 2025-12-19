from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import List, Optional, Dict, Any

class NanoBananaFileInfo(BaseModel):
    pipeline_context: str
    version: str
    target_tool: str

class NanoBananaOutputConfig(BaseModel):
    aspect_ratio: str
    resolution_px: str
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

    @field_validator('image_tasks')
    @classmethod
    def validate_unique_task_ids(cls, v: List[NanoBananaImageTask]) -> List[NanoBananaImageTask]:
        seen_ids = set()
        duplicates = []
        for task in v:
            if task.task_id in seen_ids:
                duplicates.append(task.task_id)
            seen_ids.add(task.task_id)
        
        if duplicates:
            raise ValueError(f"Duplicate task_ids found: {duplicates}")
        return v

