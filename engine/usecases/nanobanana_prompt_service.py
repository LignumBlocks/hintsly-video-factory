from typing import Optional
from domain.nanobanana_models import NanoBananaStylePresets, NanoBananaImageTask

class NanoBananaPromptService:
    def construct_prompt(self, style_presets: Optional[NanoBananaStylePresets], task: NanoBananaImageTask) -> str:
        """
        Constructs the final positive prompt.
        Order: Global Style -> Hard Rules (Implicit) -> Task Prompt
        """
        parts = []
        
        # 1. Global Image Style
        if style_presets and style_presets.global_image_style:
            parts.append(style_presets.global_image_style)
            
        # 2. Hard Rules 
        # (Reserved for future or implicit logic not currently in JSON)
        
        # 3. Task Prompt
        if task.prompt:
            parts.append(task.prompt)
            
        return " ".join(parts)

    def construct_negative_prompt(self, style_presets: Optional[NanoBananaStylePresets], task: NanoBananaImageTask) -> str:
        """
        Constructs the final negative prompt.
        Order: Global Negative -> Task Negative
        """
        parts = []
        
        # 1. Global Negative
        if style_presets and style_presets.global_negative_append:
            parts.append(style_presets.global_negative_append)
            
        # 2. Task Negative
        if task.negative_prompt:
            parts.append(task.negative_prompt)
            
        # Using comma separator for clear distinction in negative prompt
        return ", ".join(parts)
