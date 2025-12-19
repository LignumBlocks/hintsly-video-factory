import json
import sys
import os

# Add current directory to path so we can import engine modules
sys.path.append(os.getcwd())

from domain.nanobanana_models import NanoBananaImageTask, NanoBananaStylePresets
from usecases.nanobanana_prompt_service import NanoBananaPromptService

def demo_prompt_generation():
    json_path = "/home/roiky/Espacio/hintsly-video-factory/assets/catalog_files/NanoBananaPro.json"
    
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    # Extract Global Styles
    style_data = data.get("style_presets", {})
    style_presets = NanoBananaStylePresets(**style_data)
    
    # Extract First Task
    task_data = data.get("image_tasks", [])[0]
    # We need to manually handle 'approval' dict to match pydantic model if we didn't use the full request parser
    # But let's just use the Pydantic model for the task to be safe and accurate
    task = NanoBananaImageTask(**task_data)
    
    # Generate Prompts
    service = NanoBananaPromptService()
    final_prompt = service.construct_prompt(style_presets, task)
    final_negative = service.construct_negative_prompt(style_presets, task)
    
    print(f"--- Task: {task.task_id} ---")
    print("\n[GLOBAL STYLE]:", style_presets.global_image_style)
    print("\n[TASK PROMPT]:", task.prompt)
    print("\n>>> FINAL GENERATED PROMPT <<<")
    print(final_prompt)
    
    print("\n" + "="*50 + "\n")
    
    print("[GLOBAL NEGATIVE]:", style_presets.global_negative_append)
    print("\n[TASK NEGATIVE]:", task.negative_prompt)
    print("\n>>> FINAL GENERATED NEGATIVE PROMPT <<<")
    print(final_negative)

if __name__ == "__main__":
    demo_prompt_generation()
