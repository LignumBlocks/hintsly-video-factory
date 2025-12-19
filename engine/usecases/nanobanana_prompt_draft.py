from domain.nanobanana_models import NanoBananaProject, NanoBananaImageTask

class NanoBananaPromptService:
    def construct_prompt(self, project: NanoBananaProject, task: NanoBananaImageTask) -> str:
        """
        Constructs the final prompt by concatenating:
        1. style_presets.global_image_style
        2. image_task.prompt
        
        The 'hard rules' mentioned in requirements are assumed to be part of the global style
        or strictly what is present in the JSON, adhering to 'If not in JSON, it does not exist'.
        """
        parts = []
        
        # 1. Global Style
        # Accessing style_presets from project is tricky because it's passed in the Request, 
        # not necessarily inside the Project model structure depending on how we defined it.
        # Let's check the model definition.
        # NanoBananaRequest has style_presets. NanoBananaProject does NOT have style_presets in the model I defined earlier?
        # Let's double check nanobanana_models.py
        pass

    def construct_negative_prompt(self, global_negative: str, task: NanoBananaImageTask) -> str:
        parts = []
        if global_negative:
            parts.append(global_negative)
        
        if task.negative_prompt:
            parts.append(task.negative_prompt)
            
        return " ".join(parts)
