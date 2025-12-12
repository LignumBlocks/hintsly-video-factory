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

# Configure logger to see output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TestAssetsFlow(unittest.TestCase):
    def setUp(self):
        # Mocks
        self.mock_fs = MagicMock(spec=FSAdapter)
        self.mock_fs.save_image.return_value = "/tmp/mock_image.png"
        self.mock_fs.save_video.return_value = "/tmp/mock_video.mp4"
        self.mock_fs.save_metadata.return_value = "/tmp/mock_metadata.json"
        
        # We need real or mocked get_public_url logic
        # Let's use a side_effect to mimic real behavior if needed, or just return a dummy URL
        self.mock_fs.get_public_url.side_effect = lambda x: f"https://mock.url/assets/{Path(x).name}"

        self.mock_image_client = MagicMock()
        self.mock_image_client.generate.return_value = "https://mock.result/image.png"
        
        self.mock_video_client = MagicMock()
        self.mock_video_client.generate.return_value = "https://mock.result/video.mp4"
        
        # Real Services
        self.prompt_service = PromptService()
        self.logger = logging.getLogger("hintsly_test")
        
        # Real Repository with Real Config (pointing to existing files from setup)
        # Assuming run_command created the dummy file
        self.assets_repo = AssetsRepository(Config.ASSETS_CATALOG_PATH, Config.ASSETS_FILES_DIR)

    def test_asset_resolution_success(self):
        print("\n🚀 Starting test_asset_resolution_success...")
        
        # Data
        shot = Shot(
            video_id="test_video_asset",
            block_id="B01",
            shot_id="P01",
            core_flag=True,
            mv_context="LAB_WIDE", # Matches default context of LAB_ISOMETRIC_MAIN
            asset_id="LAB_ISOMETRIC_MAIN", # Known asset
            asset_mode=AssetMode.STILL_ONLY,
            camera_move="Static",
            duracion_seg=5.0,
            texto_voz_resumido="Testing assets",
            descripcion_visual="A wide shot of the lab", # Simple visual
            funcion_narrativa="Establish location"
        )
        
        # Instantiate Use Case
        usecase = ProcessShot(
            self.mock_fs,
            self.prompt_service,
            self.mock_image_client,
            self.mock_video_client,
            self.logger,
            self.assets_repo
        )
        
        # Execute
        result_shot = usecase.execute(shot)
        
        # Verification
        
        # 1. State should be COMPLETADO
        self.assertEqual(result_shot.estado, ShotEstado.COMPLETADO)
        
        # 2. Asset should be resolved in metadata
        print(f"Resolved File: {result_shot.asset_resolved_file_name}")
        print(f"Resolved Path: {result_shot.asset_resolved_path}")
        self.assertEqual(result_shot.asset_resolved_file_name, "HL_Core_Lab_Isometric_Main_v01")
        self.assertIsNotNone(result_shot.asset_resolved_path)
        self.assertTrue(str(result_shot.asset_resolved_path).endswith("HL_Core_Lab_Isometric_Main_v01.jpeg"))
        
        # 3. Prompt should contain Visual Anchor
        print(f"Generated Prompt: {result_shot.prompt_imagen}")
        self.assertIn("Visual Anchor:", result_shot.prompt_imagen)
        self.assertIn("Vista isométrica amplia del Hintsly Lab", result_shot.prompt_imagen)
        
        # 4. Image Client should be called with ref_image_url
        self.mock_image_client.generate.assert_called_once()
        args, kwargs = self.mock_image_client.generate.call_args
        
        prompt_arg = args[0]
        ref_url_arg = kwargs.get('ref_image_url')
        
        print(f"Image Client Ref URL: {ref_url_arg}")
        self.assertIsNotNone(ref_url_arg)
        self.assertIn("HL_Core_Lab_Isometric_Main_v01.jpeg", ref_url_arg)
        
        print("✅ Test Passed!")

    def test_asset_not_found_error(self):
        print("\n🚀 Starting test_asset_not_found_error...")
        
        # Data
        shot = Shot(
            video_id="test_video_asset",
            block_id="B01",
            shot_id="P02",
            core_flag=True,
            mv_context="LAB_WIDE", 
            asset_id="NON_EXISTENT_ASSET_ID",
            asset_mode=AssetMode.STILL_ONLY,
            camera_move="Static",
            duracion_seg=5.0,
            texto_voz_resumido="Testing error",
            descripcion_visual="A wide shot",
            funcion_narrativa="Fail test"
        )
        
        usecase = ProcessShot(
            self.mock_fs,
            self.prompt_service,
            self.mock_image_client,
            self.mock_video_client,
            self.logger,
            self.assets_repo
        )
        
        result_shot = usecase.execute(shot)
        
        # Should fail efficiently
        self.assertEqual(result_shot.estado, ShotEstado.ERROR)
        self.assertIn("Asset ID not found", result_shot.error_message)
        print(f"Error caught correctly: {result_shot.error_message}")
        print("✅ Test Passed!")

if __name__ == '__main__':
    unittest.main()
