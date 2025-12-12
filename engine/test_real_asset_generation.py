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
            "video_id": "csj_B02_P01_Tt", 
            "block_id": "B02_INTRO",
            "shot_id": "P01_REAL_V3",
            "core_flag": True,
            "mv_context": "LAB_MAIN",
            "asset_id": "LAB_ISOMETRIC_MAIN",
            "asset_mode": "IMAGE_1F_VIDEO", 
            "camera_move": "Zoom In",
            "duracion_seg": 8.0,
            "texto_voz_resumido": "Welcome to Hintsly Lab. We don’t promise magic; we run experiments with money and show you the math.",
            "descripcion_visual": "Wide isometric view of the full Financial War Room in dark institutional mode. Deep navy walls with a subtle blueprint grid, server racks and data screens along the sides, and a central smoked-glass table with a discreet Hintsly Lab mark glowing softly.",
            "funcion_narrativa": "Present Hintsly Lab as a serious data laboratory: not magic, but financial engineering.",
            "prompt_imagen": "Isometric 3D wide shot of a dark institutional financial war room (LAB_ISOMETRIC_MAIN). Deep navy walls with a subtle blueprint grid, server racks and data displays in the background, and a central smoked-glass table with a softly glowing abstract Hintsly Lab logo on its surface. Photorealistic, clean composition, no on-screen text.",
            "prompt_video": "Cinematic slow Zoom In...",
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
