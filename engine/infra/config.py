import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Kie.ai API settings (for Nano Banana)
    KIE_API_KEY = os.getenv("KIE_API_KEY")
    KIE_API_BASE = os.getenv("KIE_API_BASE", "https://api.kie.ai")
    KIE_NANO_BANANA_MODEL = os.getenv("KIE_NANO_BANANA_MODEL", "google/nano-banana")
    
    # Google API settings (for Veo)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_IMAGE_ENDPOINT = os.getenv("GEMINI_IMAGE_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent")
    VEO_VIDEO_ENDPOINT = os.getenv("VEO_VIDEO_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning")
    VEO_BASE_URL = os.getenv("VEO_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
