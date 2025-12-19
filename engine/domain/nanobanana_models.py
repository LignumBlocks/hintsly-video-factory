from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDict
from typing import List, Optional, Dict, Any, Union

class NanoBananaFileInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    pipeline_context: str
    version: str
    target_tool: str

class NanoBananaOutputConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    aspect_ratio: str
    resolution_px: str # Back to string (e.g. "1K", "2K", "4K")
    image_format: str

class NanoBananaProductionRules(BaseModel):
    model_config = ConfigDict(extra="allow")
    nanobanana_max_reference_images: int
    nanobanana_variants_per_image_task: int
    approval_gate: str

class NanoBananaProject(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_id: str
    title: str
    scope_blocks_included: List[str]
    output: NanoBananaOutputConfig
    production_rules: NanoBananaProductionRules

class NanoBananaStylePresets(BaseModel):
    model_config = ConfigDict(extra="allow")
    global_image_style: str
    global_negative_append: str

class NanoBananaApproval(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str

class NanoBananaImageTask(BaseModel):
    model_config = ConfigDict(extra="allow")
    task_id: str
    block_id: str
    shot_id: str
    role: str
    variants: Optional[int] = None
    refs: List[str]
    prompt: str
    negative_prompt: Optional[str] = None
    approval: NanoBananaApproval
    output: Optional[Dict[str, Any]] = None

class NanoBananaRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    file_info: Optional[NanoBananaFileInfo] = None
    project: NanoBananaProject
    asset_library: Dict[str, Any]
    naming: Optional[Dict[str, Any]] = None
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
