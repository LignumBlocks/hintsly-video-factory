import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from domain.entities import Shot
from usecases.process_shot import ProcessShot
from usecases.utils_prompt import PromptService
from adapters.fs_adapter import FSAdapter
from adapters.gemini_client import GeminiImageClient
from adapters.veo_client import VeoClient
from adapters.logger import Logger

def run_test():
    print("🚀 Starting STILL_ONLY Test (Shot Schema V2)...\n")

    # 1. Setup Dependencies
    print("📦 Initializing Adapters...")
    fs = FSAdapter()
    prompts = PromptService()
    gemini = GeminiImageClient()
    veo = VeoClient()
    logger = Logger()
    
    # 2. Setup Use Case
    print("⚙️  Initializing ProcessShot Use Case...")
    process_uc = ProcessShot(fs, prompts, gemini, veo, logger)

    # 3. Create Shot V2 with STILL_ONLY mode
    shot_data = {
        "video_id": "test_still_001",
        "block_id": "B02_CONTENT",
        "shot_id": "P05",
        "core_flag": True,
        "mv_context": "MINIMALIST",
        "asset_mode": "STILL_ONLY",  # Only image, no video
        "camera_move": "Static",
        "duracion_seg": 5.0,
        "texto_voz_resumido": "A peaceful moment",
        "descripcion_visual": "A serene mountain landscape at sunset",
        "funcion_narrativa": "Create a calm, contemplative mood",
        "estado": "PENDIENTE"
    }
    shot = Shot(**shot_data)
    print(f"\n📝 Created Shot V2: {shot.video_id}/{shot.block_id}/{shot.shot_id}")
    print(f"   Visual: {shot.descripcion_visual}")
    print(f"   Asset Mode: {shot.asset_mode} (should skip video generation)")

    # 4. Execute ProcessShot
    print("\n▶️  Executing ProcessShot...")
    processed_shot = process_uc.execute(shot)
    
    print("\n✅ ProcessShot Result:")
    print(f"   State: {processed_shot.estado}")
    print(f"   Image Path: {processed_shot.image_path}")
    print(f"   Video Path: {processed_shot.video_path} (should be None)")
    
    # 5. Verify expectations
    if processed_shot.video_path is None:
        print("\n✅ PASS: Video was correctly skipped for STILL_ONLY mode")
    else:
        print("\n❌ FAIL: Video should not have been generated for STILL_ONLY mode")
    
    if processed_shot.image_path:
        print("✅ PASS: Image was generated as expected")
    else:
        print("❌ FAIL: Image should have been generated")

    print("\n🎉 STILL_ONLY Test Completed!")

if __name__ == "__main__":
    run_test()
