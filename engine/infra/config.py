import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Kie.ai API settings (for Nano Banana and Veo)
    KIE_API_KEY = os.getenv("KIE_API_KEY")
    KIE_API_BASE = os.getenv("KIE_API_BASE", "https://api.kie.ai")
    KIE_NANO_BANANA_MODEL = os.getenv("KIE_NANO_BANANA_MODEL", "nano-banana-pro")
    KIE_VEO_MODEL = os.getenv("KIE_VEO_MODEL", "veo3_fast")  # Correct model name: veo3_fast
    
    # Public URL configuration (for serving assets)
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://engine.srv954959.hstgr.cloud")
    
    # Asset Configuration
    # Default to the known location in context folder for catalog, and assets/catalog_files for images
    ASSETS_CATALOG_PATH = os.getenv("ASSETS_CATALOG_PATH", "/home/roiky/Espacio/hintsly-video-factory/assets/catalog_files/assets.json")
    ASSETS_FILES_DIR = os.getenv("ASSETS_FILES_DIR", "/home/roiky/Espacio/hintsly-video-factory/assets/catalog_files")
    
    # Google API settings (legacy/fallback)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
