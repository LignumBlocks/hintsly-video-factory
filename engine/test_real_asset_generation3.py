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
            "video_id": "csj_B01_P02",
            "block_id": "B01_HOOK",
            "shot_id": "P02",
            "core_flag": True,
            "mv_context": "LAB_TABLE",
            "asset_id": "LAB_CREDITSYSTEM_TABLE",
            "asset_mode": "IMAGE_1F_VIDEO",
            "camera_move": "Zoom In",
            "duracion_seg": 8.0,
            "texto_voz_resumido": "Person A buys a twenty-five-thousand-dollar car with a 650 score. Person B buys the exact same car with a 710 score. Same car. Same job. Same income.",
            "descripcion_visual": "Isometric view of the central credit system table in the Financial War Room. On the smoked-glass surface there are two identical matte black data modules labeled visually as Person A and Person B (no readable text), each with a single teal cable running towards a vertical risk structure in the background.",
            "funcion_narrativa": "Introduce the cold system that sees two almost identical people as two different routes only because of their score band.",
            "prompt_imagen": "Isometric 3D view of a dark institutional financial command table (LAB_CREDITSYSTEM_TABLE). Two identical matte black data modules represent Person A and Person B, each connected by a single glowing teal fiber-optic cable toward a vertical stack of risk-band blocks. Deep navy background, subtle blueprint grid, photorealistic, no on-screen text.",
            "prompt_video": "Cinematic slow Zoom In towards the center of the credit system table, moving closer to the two data modules and their teal cables while small status lights and data pulses move gently inside the system. Camera is stable and smooth, no frantic motion.",
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
