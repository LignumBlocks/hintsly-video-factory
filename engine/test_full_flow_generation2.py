import logging
import sys
import unittest
from pathlib import Path

# Add engine to path
sys.path.append(str(Path(__file__).parent))

from domain.entities import Shot, AssetMode, ShotEstado
from usecases.process_shot import ProcessShot
from usecases.utils_prompt import PromptService
from adapters.fs_adapter import FSAdapter
from adapters.assets_repository import AssetsRepository
from adapters.gemini_client import GeminiImageClient
from adapters.veo_client import KieVeoClient
from infra.config import Config

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TestFullFlowGeneration(unittest.TestCase):
    def setUp(self):
        # 1. Real FS Adapter
        self.fs_adapter = FSAdapter()
        
        # 2. Real Prompt Service
        self.prompt_service = PromptService()
        
        # 3. Real Image Client (Nano Banana Pro)
        self.image_client = GeminiImageClient()
        
        # 4. REAL Video Client (Veo)
        self.video_client = KieVeoClient()
        
        # 5. Real Assets Repository
        self.assets_repo = AssetsRepository(Config.ASSETS_CATALOG_PATH, Config.ASSETS_FILES_DIR)
        
        self.logger = logging.getLogger("full_flow_test")

    def test_full_pipeline_generation(self):
        print("\n🚀 Starting FULL FLOW Generation Test (Image + Video) with VACA asset...")
        
        # User Provided JSON Data
        # Using "vaca" asset since we verified it works for image generation
        # And requesting IMAGE_1F_VIDEO to trigger video generation
        shot_data = {
                "video_id": "csj_B01_P03",
                "block_id": "B01_HOOK",
                "shot_id": "P03",
                "core_flag": True,
                "mv_context": "LAB_FLOATING",
                "asset_id": "CREDIT_STAIRCASE_SIDE",
                "asset_mode": "IMAGE_1F_VIDEO",
                "camera_move": "Tilt Up / Tilt Down",
                "duracion_seg": 8.0,
                "texto_voz_resumido": "Over five years, Person A pays about seven thousand dollars in interest. Person B pays under four thousand seven hundred. That’s roughly two thousand three hundred dollars gone — just because, the week the bank ran the numbers, they landed in a different score band.",
                "descripcion_visual": "Isometric glass staircase representing score bands seen from a side angle. Lower steps glow soft amber, higher steps glow soft green. On one amber step, a small glass panel shows a higher monthly payment and red total interest; on a higher green step, another panel shows a slightly lower payment and green total interest.",
                "funcion_narrativa": "Visualize that the system works in steps: one small score change can move you to a different price band with a totally different cost.",
                "prompt_imagen": "Isometric 3D glass staircase in a dark financial lab, lower steps glowing soft amber and higher steps glowing soft green. On an amber step, a glass panel shows a higher payment and a red-tinted total interest. On a green step above, another panel shows a lower payment and a green-tinted total interest. Deep navy background, subtle blueprint grid, photorealistic, clean composition.",
                "prompt_video": "Slow Tilt Up camera move starting from the lower amber steps, then rising to reveal the higher green steps and the two contrasting payment/interest panels. Teal data lines pulse gently along the staircase while everything stays readable.",
                "image_path": "",
                "video_path": "",
                "estado": "PENDIENTE",
                "error_message": None

        }
        
        # Convert to Entity
        shot = Shot(**shot_data)
        
        usecase = ProcessShot(
            self.fs_adapter,
            self.prompt_service,
            self.image_client,
            self.video_client,
            self.logger,
            self.assets_repo
        )
        
        # --- REMOTE ACCESS FOR LOCAL TESTING (NGROK) ---
        # We use the Ngrok public URL to expose our local files to the remote Kie.ai API.
        # Python HTTP server is running at project root (port 8000).
        ngrok_url = "https://ea40c095f84d.ngrok-free.app"
        
        print(f"🔧 Patching video_client to use Ngrok: {ngrok_url} ...")
        
        def local_to_public(path):
            # Convert /home/roiky/.../assets/... -> assets/...
            try:
                path_str = str(path)
                if "/assets/" in path_str:
                    rel_path = path_str.split("/assets/", 1)[1]
                    return f"{ngrok_url}/assets/{rel_path}"
                return path 
            except Exception as e:
                print(f"URL conversion error: {e}")
                return path

        self.video_client._get_public_image_url = local_to_public
        
        # Execute
        print("▶️ Executing ProcessShot with Real Image AND Real Video APIs...")
        result = usecase.execute(shot)
        
        # Verification
        print("\n📊 Results:")
        print(f"State: {result.estado}")
        if result.error_message:
            print(f"Error Message: {result.error_message}")
            
        print(f"Resolved Asset: {result.asset_resolved_file_name}")
        print(f"Image Path: {result.image_path}")
        print(f"Video Path: {result.video_path}")
        
        # Assertions
        self.assertEqual(result.estado, ShotEstado.COMPLETADO)
        self.assertIsNotNone(result.image_path)
        self.assertIsNotNone(result.video_path)
        
        # Verify files exist
        image_file = Path(result.image_path)
        video_file = Path(result.video_path)
        
        self.assertTrue(image_file.exists(), "Image file should exist")
        self.assertGreater(image_file.stat().st_size, 0, "Image file should not be empty")
        
        self.assertTrue(video_file.exists(), "Video file should exist")
        self.assertGreater(video_file.stat().st_size, 0, "Video file should not be empty")
        
        print("✅ Full Flow Generation Test Passed!")

if __name__ == '__main__':
    unittest.main()
