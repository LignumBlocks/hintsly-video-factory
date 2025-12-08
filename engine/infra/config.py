import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_IMAGE_ENDPOINT = os.getenv("GEMINI_IMAGE_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent")
    VEO_VIDEO_ENDPOINT = os.getenv("VEO_VIDEO_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning")
    VEO_BASE_URL = os.getenv("VEO_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
