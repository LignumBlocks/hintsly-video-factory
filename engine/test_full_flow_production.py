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

class TestFullFlowProduction(unittest.TestCase):
    """
    Production-ready integration test for the full video generation pipeline.
    
    This test does NOT use Ngrok or any monkey patching. It relies on:
    1. PUBLIC_BASE_URL being correctly configured in .env
    2. The assets directory being publicly accessible via HTTP/HTTPS
    3. The veo_client._get_public_image_url() method working as designed
    
    Use this test in staging/production environments where files are served
    by a real web server (Nginx, Apache, etc.)
    """
    
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
        
        self.logger = logging.getLogger("full_flow_production_test")

    def test_full_pipeline_generation(self):
        print("\n🚀 Starting PRODUCTION Full Flow Test (Image + Video)...")
        print(f"📡 PUBLIC_BASE_URL: {Config.PUBLIC_BASE_URL}")
        
        # User Provided JSON Data
        shot_data = {
            "video_id": "prod_test_B01_P02",
            "block_id": "B01_HOOK",
            "shot_id": "P02",
            "core_flag": True,
            "mv_context": "LAB_TABLE",
            "asset_id": "LAB_CREDITSYSTEM_TABLE",
            "asset_mode": "IMAGE_1F_VIDEO",
            "camera_move": "zoom_in",
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
            self.video_client,
            self.logger,
            self.assets_repo
        )
        
        # --- NO MONKEY PATCHING ---
        # The video_client will use its native _get_public_image_url() method
        # which constructs URLs based on Config.PUBLIC_BASE_URL
        
        # Execute
        print("▶️ Executing ProcessShot with Real APIs (Production Mode)...")
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
        self.assertEqual(result.estado, ShotEstado.COMPLETADO, 
                        f"Expected COMPLETADO but got {result.estado}. Error: {result.error_message}")
        self.assertIsNotNone(result.image_path, "Image path should not be None")
        self.assertIsNotNone(result.video_path, "Video path should not be None")
        
        # Verify files exist
        image_file = Path(result.image_path)
        video_file = Path(result.video_path)
        
        self.assertTrue(image_file.exists(), f"Image file should exist at {result.image_path}")
        self.assertGreater(image_file.stat().st_size, 0, "Image file should not be empty")
        
        self.assertTrue(video_file.exists(), f"Video file should exist at {result.video_path}")
        self.assertGreater(video_file.stat().st_size, 0, "Video file should not be empty")
        
        print("✅ Production Full Flow Test Passed!")
        print(f"📁 Output directory: {image_file.parent}")

if __name__ == '__main__':
    unittest.main()
