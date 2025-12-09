import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Kie.ai API settings (for Nano Banana and Veo)
    KIE_API_KEY = os.getenv("KIE_API_KEY")
    KIE_API_BASE = os.getenv("KIE_API_BASE", "https://api.kie.ai")
    KIE_NANO_BANANA_MODEL = os.getenv("KIE_NANO_BANANA_MODEL", "google/nano-banana")
    KIE_VEO_MODEL = os.getenv("KIE_VEO_MODEL", "veo3_fast")  # Correct model name: veo3_fast
    
    # Public URL configuration (for serving assets)
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://engine.srv954959.hstgr.cloud")
    
    # Google API settings (legacy/fallback)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
   

