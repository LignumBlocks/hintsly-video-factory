import logging
import sys
import unittest
from unittest.mock import MagicMock
from pathlib import Path

# Add engine to path
sys.path.append(str(Path(__file__).parent))

from domain.entities import Shot, AssetMode, ShotEstado
from usecases.process_shot import ProcessShot
from usecases.utils_prompt import PromptService
from adapters.fs_adapter import FSAdapter
from adapters.assets_repository import AssetsRepository
from adapters.gemini_client import GeminiImageClient
from infra.config import Config

# Configure logger to see output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TestRealAssetGeneration(unittest.TestCase):
    def setUp(self):
        # 1. Real FS Adapter
        self.fs_adapter = FSAdapter()
        
        # 2. Real Prompt Service
        self.prompt_service = PromptService()
        
        # 3. Real Image Client (Kie.ai)
        self.image_client = GeminiImageClient()
        
        # 4. Mock Video Client (Skipping video generation as requested)
        self.mock_video_client = MagicMock()
        self.mock_video_client.generate.return_value = "https://mock.result/skipped_video.mp4"
        
        # 5. Real Assets Repository
        self.assets_repo = AssetsRepository(Config.ASSETS_CATALOG_PATH, Config.ASSETS_FILES_DIR)
        
        self.logger = logging.getLogger("real_gen_test")

    def test_real_lab_isometric_generation(self):
        print("\n🚀 Starting REAL Generation Test (LAB_ISOMETRIC_MAIN) with PRE-UPLOADED PUBLIC ASSET...")
        
        # User Provided JSON Data
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
            self.mock_video_client,
            self.logger,
            self.assets_repo
        )
        
        # Execute
        print("▶️ Executing ProcessShot with Real Image API...")
        result = usecase.execute(shot)
        
        # Verification
        print("\n📊 Results:")
        print(f"State: {result.estado}")
        if result.error_message:
            print(f"Error Message: {result.error_message}")
            
        print(f"Resolved Asset: {result.asset_resolved_file_name}")
        print(f"Resolved Path: {result.asset_resolved_path}")
        print(f"Context Mismatch: {result.asset_mv_context_mismatch}")
        
        print(f"Image Path: {result.image_path}")
        
        # Assertions
        self.assertEqual(result.estado, ShotEstado.COMPLETADO)
        self.assertIsNotNone(result.image_path)
        
        # Verify image file actually exists and has size
        image_file = Path(result.image_path)
        self.assertTrue(image_file.exists())
        self.assertGreater(image_file.stat().st_size, 0)
        
        print("✅ Real Generation Test Passed!")

if __name__ == '__main__':
    unittest.main()
