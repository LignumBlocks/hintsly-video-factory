import sys
import os
import json

# Add current directory to path
sys.path.append(os.getcwd())

from domain.entities import Shot
from usecases.process_shot import ProcessShot
from usecases.regenerate_shot import RegenerateShot
from usecases.utils_prompt import PromptService
from adapters.fs_adapter import FSAdapter
from adapters.gemini_client import GeminiClient
from adapters.veo_client import VeoClient
from adapters.logger import Logger

def run_test():
    print("🚀 Starting Engine Test Flow...\n")

    # 1. Setup Dependencies
    print("📦 Initializing Adapters...")
    fs = FSAdapter()
    prompts = PromptService()
    gemini = GeminiClient()
    veo = VeoClient()
    logger = Logger()
    
    # 2. Setup Use Cases
    print("⚙️  Initializing Use Cases...")
    process_uc = ProcessShot(fs, prompts, gemini, veo)
    regenerate_uc = RegenerateShot(process_uc)

    # 3. Create Dummy Shot
    shot_data = {
        "video_id": "test_video_001",
        "bloque": "1",
        "plano": 1,
        "descripcion_visual": "A futuristic city with flying cars",
        "movimiento_camara": "Pan right",
        "estado": "PENDIENTE"
    }
    shot = Shot(**shot_data)
    print(f"\n📝 Created Shot: {shot.video_id} | Block {shot.bloque} | Shot {shot.plano}")
    print(f"   Visual: {shot.descripcion_visual}")

    # 4. Execute ProcessShot
    print("\n▶️  Executing ProcessShot...")
    processed_shot = process_uc.execute(shot)
    
    print("\n✅ ProcessShot Result:")
    print(f"   State: {processed_shot.estado}")
    print(f"   Image Prompt: {processed_shot.prompt_imagen}")
    print(f"   Video Prompt: {processed_shot.prompt_video}")
    print(f"   Image Path: {processed_shot.image_path}")
    print(f"   Video Path: {processed_shot.video_path}")

    # 5. Execute RegenerateShot
    print("\n🔄 Executing RegenerateShot...")
    # Modify something to see if it persists or resets (logic says it resets prompts/paths)
    regenerated_shot = regenerate_uc.execute(processed_shot)

    print("\n✅ RegenerateShot Result:")
    print(f"   State: {regenerated_shot.estado}")
    print(f"   Image Path (should be new/overwritten): {regenerated_shot.image_path}")
    print(f"   Video Path (should be new/overwritten): {regenerated_shot.video_path}")

    print("\n🎉 Test Flow Completed Successfully!")

if __name__ == "__main__":
    run_test()
