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
from adapters.gemini_client import GeminiImageClient
from adapters.veo_client import VeoClient
from adapters.logger import Logger

def run_test():
    print("🚀 Starting Engine Test Flow (Shot Schema V2)...\n")

    # 1. Setup Dependencies
    print("📦 Initializing Adapters...")
    fs = FSAdapter()
    prompts = PromptService()
    gemini = GeminiImageClient()
    veo = VeoClient()
    logger = Logger()
    
    # 2. Setup Use Cases
    print("⚙️  Initializing Use Cases...")
    process_uc = ProcessShot(fs, prompts, gemini, veo, logger)
    regenerate_uc = RegenerateShot(process_uc)

    # 3. Create Shot V2
    shot_data = {
        "video_id": "test_video_001",
        "block_id": "B01_HOOK",
        "shot_id": "P01",
        "core_flag": False,
        "mv_context": "REAL_CHAOS",
        "asset_mode": "IMAGE_1F_VIDEO",
        "camera_move": "Handheld",
        "duracion_seg": 8.0,
        "texto_voz_resumido": "Introduction to the chaotic scene",
        "descripcion_visual": "A futuristic city with flying cars and neon lights",
        "funcion_narrativa": "Establish the setting and mood",
        "estado": "PENDIENTE"
    }
    shot = Shot(**shot_data)
    print(f"\n📝 Created Shot V2: {shot.video_id}/{shot.block_id}/{shot.shot_id}")
    print(f"   Visual: {shot.descripcion_visual}")
    print(f"   Asset Mode: {shot.asset_mode}")
    print(f"   MV Context: {shot.mv_context}")

    # 4. Execute ProcessShot
    print("\n▶️  Executing ProcessShot...")
    processed_shot = process_uc.execute(shot)
    
    print("\n✅ ProcessShot Result:")
    print(f"   State: {processed_shot.estado}")
    print(f"   Image Prompt: {processed_shot.prompt_imagen[:80] if processed_shot.prompt_imagen else 'None'}...")
    print(f"   Video Prompt: {processed_shot.prompt_video[:80] if processed_shot.prompt_video else 'None'}...")
    print(f"   Image Path: {processed_shot.image_path}")
    print(f"   Video Path: {processed_shot.video_path}")

    # 5. Execute RegenerateShot
    print("\n🔄 Executing RegenerateShot...")
    regenerated_shot = regenerate_uc.execute(processed_shot)

    print("\n✅ RegenerateShot Result:")
    print(f"   State: {regenerated_shot.estado}")
    print(f"   Image Path (should be new/overwritten): {regenerated_shot.image_path}")
    print(f"   Video Path (should be new/overwritten): {regenerated_shot.video_path}")

    print("\n🎉 Test Flow Completed Successfully!")

if __name__ == "__main__":
    run_test()
