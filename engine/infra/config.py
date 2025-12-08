import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_IMAGE_ENDPOINT = os.getenv("GEMINI_IMAGE_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent")
