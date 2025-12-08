import requests
import json
from infra.config import Config
from domain.errors import ImageGenerationError, PromptError
from adapters.logger import Logger

logger = Logger()

class GeminiImageClient:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.endpoint = Config.GEMINI_IMAGE_ENDPOINT
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables.")

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise ImageGenerationError("GEMINI_API_KEY is missing")

        if not prompt:
            raise PromptError("Prompt cannot be empty")

        url = f"{self.endpoint}?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Payload structure for Gemini generateContent
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            # Optional: Add generationConfig if needed for image params
        }

        try:
            logger.info(f"Sending request to Gemini Image API for prompt: {prompt[:30]}...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # TODO: Inspect actual response structure for Gemini Image Generation
            # This is a naive implementation assuming it might return inline data or an error
            # We will use the verification script to inspect the actual JSON and adjust.
            
            # Check for candidates
            if "candidates" not in data or not data["candidates"]:
                raise ImageGenerationError(f"No candidates returned: {data}")
            
            try:
                # Expecting base64 data in inline_data or similar
                # Just returning raw data for now to inspect in verify script if structure is unknown
                # But for the adapter contract, we need to return a string (url or base64)
                
                # Common Gemini structure for text:
                # candidate = data["candidates"][0]
                # part = candidate["content"]["parts"][0]
                # text = part["text"]
                
                # For Image, it complicates things. Let's try to find inline_data
                candidate = data["candidates"][0]
                # Traverse parts
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part:
                             # It's base64
                             mime_type = part["inlineData"]["mimeType"] # e.g. "image/png"
                             b64_data = part["inlineData"]["data"]
                             return f"data:{mime_type};base64,{b64_data}"
                        if "text" in part:
                            # It might have refused or returned text description
                            logger.warning(f"Gemini returned text instead of image: {part['text']}")
                
                # If we get here, we didn't find an image
                raise ImageGenerationError("No image data found in response")

            except KeyError as e:
                raise ImageGenerationError(f"Unexpected response structure: {e}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {e}")
            if e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise ImageGenerationError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Error during image generation: {e}")
            raise ImageGenerationError(str(e))
