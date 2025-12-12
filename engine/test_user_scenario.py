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
from infra.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TestUserScenario(unittest.TestCase):
    def setUp(self):
        self.mock_fs = MagicMock(spec=FSAdapter)
        self.mock_fs.save_image.return_value = "/tmp/mock_image.png"
        self.mock_fs.save_video.return_value = "/tmp/mock_video.mp4"
        self.mock_fs.save_metadata.return_value = "/tmp/mock_metadata.json"
        self.mock_fs.get_public_url.side_effect = lambda x: f"https://mock.url/assets/{Path(x).name}"

        self.mock_image_client = MagicMock()
        self.mock_image_client.generate.return_value = "https://mock.result/image.png"
        
        self.mock_video_client = MagicMock()
        self.mock_video_client.generate.return_value = "https://mock.result/video.mp4"
        
        self.prompt_service = PromptService()
        self.logger = logging.getLogger("user_scenario_test")
        
        self.assets_repo = AssetsRepository(Config.ASSETS_CATALOG_PATH, Config.ASSETS_FILES_DIR)

    def test_lab_isometric_main_scenario(self):
        print("\n🚀 Starting User Scenario Test (LAB_ISOMETRIC_MAIN)...")
        
        # User Provided JSON Data
        shot_data = {
            "video_id": "csj_B02_P01",
            "block_id": "B02_INTRO",
            "shot_id": "P01",
            "core_flag": True,
            "mv_context": "LAB_MAIN",  # Note: Mismatch expected (Default is LAB_WIDE)
            "asset_id": "LAB_ISOMETRIC_MAIN",
            "asset_mode": "IMAGE_1F_VIDEO",
            "camera_move": "Zoom In",
            "duracion_seg": 8.0,
            "texto_voz_resumido": "Welcome to Hintsly Lab...",
            "descripcion_visual": "Wide isometric view...",
            "funcion_narrativa": "Present Hintsly Lab...",
            "prompt_imagen": "Isometric 3D wide shot of a dark institutional financial war room...",
            "prompt_video": "Cinematic slow Zoom In...",
            "estado": "PENDIENTE"
        }
        
        # Convert to Entity
        shot = Shot(**shot_data)
        
        usecase = ProcessShot(
            self.mock_fs,
            self.prompt_service,
            self.mock_image_client,
            self.mock_video_client,
            self.logger,
            self.assets_repo
        )
        
        # Execute
        result = usecase.execute(shot)
        
        # Assertions
        
        # 1. Asset Resolution
        print(f"Asset Resolved: {result.asset_resolved_file_name}")
        self.assertEqual(result.asset_resolved_file_name, "HL_Core_Lab_Isometric_Main_v01")
        
        # 2. Context Mismatch
        print(f"Context Mismatch: {result.asset_mv_context_mismatch}")
        self.assertTrue(result.asset_mv_context_mismatch, "Should detect mismatch between LAB_MAIN and LAB_WIDE")
        
        # 3. Reference Image Usage
        # Check that image client was called with ref_image_url
        args, kwargs = self.mock_image_client.generate.call_args
        ref_url = kwargs.get('ref_image_url')
        print(f"Ref URL used: {ref_url}")
        self.assertIsNotNone(ref_url)
        self.assertIn("HL_Core_Lab_Isometric_Main_v01.jpeg", ref_url)
        
        # 4. Prompt Preservation
        # Ensure the manually provided prompt was NOT overwritten (no "Visual Anchor" appended)
        # Because the code logic is `if not shot.prompt_imagen`
        print(f"Final Prompt: {result.prompt_imagen}")
        self.assertNotIn("Visual Anchor:", result.prompt_imagen)
        self.assertEqual(result.prompt_imagen, shot_data["prompt_imagen"])
        
        # 5. Video Generation
        # User data said IMAGE_1F_VIDEO, so it should have tried to generate video
        # (Mock verified)
        self.mock_video_client.generate.assert_called_once()
        print("Video generation attempted (as per asset_mode IMAGE_1F_VIDEO)")
        
        print("✅ User Scenario Test Passed!")

if __name__ == '__main__':
    unittest.main()
