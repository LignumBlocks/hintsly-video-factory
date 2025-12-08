import time
import base64
import requests
from adapters.logger import Logger
from domain.errors import VideoGenerationError
from infra.config import Config

logger = Logger()

class VeoClient:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY  # Veo uses the same API key as Gemini
        self.endpoint = Config.VEO_VIDEO_ENDPOINT
        self.base_url = Config.VEO_BASE_URL
        self.poll_interval = 10  # seconds
        self.max_polls = 60  # max ~10 minutes of polling
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found - Veo video generation will fail")

    def generate(self, image_path: str, prompt_video: str) -> str:
        """
        Generate video using Veo 3.1 API with image-to-video.
        
        Args:
            image_path: Path to the image file on disk
            prompt_video: Text prompt for video generation
            
        Returns:
            Data URI string with base64 encoded video or URL to download
        """
        if not self.api_key:
            raise VideoGenerationError("GEMINI_API_KEY is missing for Veo")

        if not image_path:
            raise VideoGenerationError("Image path is required for image-to-video generation")

        try:
            # Step 1: Read and encode the image
            logger.info(f"Reading image from: {image_path}")
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Determine mime type from file extension
            mime_type = "image/jpeg"
            if image_path.endswith(".png"):
                mime_type = "image/png"
            elif image_path.endswith(".webp"):
                mime_type = "image/webp"

            # Step 2: Submit the generation job
            operation_name = self._submit_job(image_b64, mime_type, prompt_video)
            
            # Step 3: Poll until completion
            video_uri = self._poll_until_complete(operation_name)
            
            # Step 4: Download the video
            video_data = self._download_video(video_uri)
            
            return video_data

        except VideoGenerationError:
            raise
        except Exception as e:
            logger.error(f"Veo generation failed: {e}")
            raise VideoGenerationError(f"Video generation failed: {e}")

    def _submit_job(self, image_b64: str, mime_type: str, prompt: str) -> str:
        """Submit video generation job to Veo API."""
        url = f"{self.endpoint}?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Payload for image-to-video generation
        payload = {
            "instances": [{
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": image_b64,
                    "mimeType": mime_type
                }
            }]
        }
        
        logger.info(f"Submitting Veo job with prompt: {prompt[:50]}...")
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            error_msg = response.text
            logger.error(f"Veo API error: {error_msg}")
            raise VideoGenerationError(f"Veo API returned {response.status_code}: {error_msg}")
        
        data = response.json()
        operation_name = data.get("name")
        
        if not operation_name:
            raise VideoGenerationError(f"No operation name in response: {data}")
        
        logger.info(f"Veo job submitted: {operation_name}")
        return operation_name

    def _poll_until_complete(self, operation_name: str) -> str:
        """Poll the operation status until video is ready."""
        poll_url = f"{self.base_url}/{operation_name}?key={self.api_key}"
        
        for attempt in range(self.max_polls):
            logger.info(f"Polling Veo job (attempt {attempt + 1}/{self.max_polls})...")
            
            response = requests.get(poll_url, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Poll returned {response.status_code}: {response.text}")
                time.sleep(self.poll_interval)
                continue
            
            data = response.json()
            
            # Check if done
            if data.get("done") is True:
                logger.info("Veo job completed!")
                
                # Extract video URI from response
                try:
                    video_uri = data["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
                    return video_uri
                except KeyError as e:
                    logger.error(f"Unexpected response structure: {data}")
                    raise VideoGenerationError(f"Could not extract video URI: {e}")
            
            # Check for error
            if "error" in data:
                error = data["error"]
                raise VideoGenerationError(f"Veo job failed: {error}")
            
            time.sleep(self.poll_interval)
        
        raise VideoGenerationError(f"Veo job timed out after {self.max_polls * self.poll_interval} seconds")

    def _download_video(self, video_uri: str) -> str:
        """Download video from URI and return as data URI."""
        logger.info(f"Downloading video from: {video_uri[:50]}...")
        
        # The video URI requires the API key for authentication
        download_url = f"{video_uri}&key={self.api_key}" if "?" in video_uri else f"{video_uri}?key={self.api_key}"
        
        response = requests.get(download_url, timeout=120, allow_redirects=True)
        
        if response.status_code != 200:
            raise VideoGenerationError(f"Failed to download video: {response.status_code}")
        
        # Return as data URI for consistency with image handling
        video_bytes = response.content
        video_b64 = base64.b64encode(video_bytes).decode("utf-8")
        
        logger.info(f"Video downloaded: {len(video_bytes)} bytes")
        
        return f"data:video/mp4;base64,{video_b64}"
