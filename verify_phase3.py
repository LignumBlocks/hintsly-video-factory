import sys
import os
import shutil
from pathlib import Path

# Add engine to path
sys.path.append(os.path.join(os.getcwd(), "engine"))

from engine.domain.entities import Shot
from engine.usecases.process_shot import ProcessShot
from engine.usecases.utils_prompt import PromptService
from engine.adapters.fs_adapter import FSAdapter
from engine.adapters.gemini_client import GeminiImageClient
from engine.adapters.veo_client import VeoClient
from engine.adapters.logger import Logger
from dotenv import load_dotenv

# Load env variables for Gemini
load_dotenv()

def verify_phase3():
    print("🚀 Starting Phase 3 Verification...")

    # Cleanup previous test data
    test_video_id = "test_phase3_v1"
    assets_dir = Path("assets/videos") / test_video_id
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
        print(f"🧹 Cleaned up {assets_dir}")

    # Initialize components
    logger = Logger()
    fs = FSAdapter()
    prompts = PromptService()
    gemini = GeminiImageClient()
    veo = VeoClient()
    
    # Update veo client for the test to be faster if possible (methods are not configurable but that's fine)

    usecase = ProcessShot(fs, prompts, gemini, veo, logger)

    # Create a test shot
    shot = Shot(
        video_id=test_video_id,
        bloque="1",
        plano=1,
        descripcion_visual="A cybernetic cat sitting on a neon roof in Tokyo",
        movimiento_camara="Slow pan to the right"
    )

    print(f"🎬 Processing shot: {shot.descripcion_visual}")
    
    # Execute
    try:
        result_shot = usecase.execute(shot)
    except Exception as e:
        print(f"❌ Execution failed with exception: {e}")
        return

    # Check result
    print(f"✅ Shot status: {result_shot.estado}")
    if result_shot.estado == "ERROR":
        print(f"❌ Error message: {result_shot.error_message}")
        return

    # Verify files
    files_to_check = [
        result_shot.image_path,
        result_shot.video_path,
        str(Path(result_shot.image_path).parent / "metadata.json")
    ]
    
    all_exist = True
    for fpath in files_to_check:
        if fpath and os.path.exists(fpath):
            print(f"✅ Found file: {fpath} ({os.path.getsize(fpath)} bytes)")
        else:
            print(f"❌ Missing file: {fpath}")
            all_exist = False

    if all_exist:
        print("\n✨ Phase 3 Verification SUCCESSFUL! ✨")
    else:
        print("\n⚠️  Phase 3 Verification completed with MISSING FILES.")

if __name__ == "__main__":
    verify_phase3()
