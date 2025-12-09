import time
import base64
import requests
import json
from adapters.logger import Logger
from domain.errors import VideoGenerationError
from infra.config import Config

logger = Logger()

class KieVeoClient:
    """
    Client for Kie.ai Veo API (veo3 / veo3-1-fast).
    Uses async task-based API with polling.
    """
    
    def __init__(self):
        self.api_key = Config.KIE_API_KEY
        self.base_url = Config.KIE_API_BASE
        self.model = Config.KIE_VEO_MODEL
        self.poll_interval = 10  # seconds
        self.max_polls = 60  # max ~10 minutes
        
        if not self.api_key:
            logger.warning("KIE_API_KEY not found - Veo video generation will fail")

    def generate(self, image_path: str, prompt_video: str) -> str:
        """
        Generate video using Kie.ai Veo API with image-to-video.
        
        Args:
            image_path: Path to the image file on disk
            prompt_video: Text prompt for video generation
            
        Returns:
            Data URI string with base64 encoded video
        """
        if not self.api_key:
            raise VideoGenerationError("KIE_API_KEY is missing for Veo")

        if not image_path:
            raise VideoGenerationError("Image path is required for image-to-video generation")

        try:
            # Step 1: Upload image and get URL (or use direct upload if supported)
            # For now, we'll need to upload the image to a publicly accessible URL
            # This is a limitation - Kie.ai requires image URLs, not base64
            logger.warning("Kie.ai Veo requires image URLs. Using local path workaround...")
            
            # Step 2: Submit the generation job
            task_id = self._submit_job(image_path, prompt_video)
            
            # Step 3: Poll until completion
            video_url = self._poll_until_complete(task_id)
            
            # Step 4: Download the video
            video_data = self._download_video(video_url)
            
            return video_data

        except VideoGenerationError:
            raise
        except Exception as e:
            logger.error(f"Kie.ai Veo generation failed: {e}")
            raise VideoGenerationError(f"Video generation failed: {e}")

    def _submit_job(self, image_path: str, prompt: str) -> str:
        """Submit video generation job to Kie.ai Veo API."""
        url = f"{self.base_url}/api/v1/veo/generate"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Convert local image path to public URL
        image_url = self._get_public_image_url(image_path)
        
        payload = {
            "prompt": prompt,
            "model": self.model,
            "aspectRatio": "16:9",
            "imageUrls": [image_url]
        }

        print(f" Estee es el modelooo {self.model}")
        
        logger.info(f"Submitting Kie.ai Veo job with prompt: {prompt[:50]}...")
        logger.info(f"Image URL: {image_url}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            error_msg = response.text
            logger.error(f"Kie.ai Veo API error: {error_msg}")
            raise VideoGenerationError(f"Kie.ai Veo API returned {response.status_code}: {error_msg}")
        
        data = response.json()
        
        if data.get("code") != 200:
            raise VideoGenerationError(f"Kie.ai Veo error: {data.get('msg')}")
        
        task_id = data.get("data", {}).get("taskId")
        
        if not task_id:
            raise VideoGenerationError(f"No taskId in response: {data}")
        
        logger.info(f"Kie.ai Veo task created: {task_id}")
        return task_id
    
    def _get_public_image_url(self, image_path: str) -> str:
        """Convert local image path to public URL."""
        from pathlib import Path
        from infra.paths import ASSETS_DIR
        
        # Convert to Path object
        img_path = Path(image_path)
        assets_path = Path(ASSETS_DIR)
        
        # Get relative path from assets directory
        try:
            relative_path = img_path.relative_to(assets_path)
        except ValueError:
            raise VideoGenerationError(f"Image path {image_path} is not within assets directory")
        
        # Construct public URL
        public_url = f"{Config.PUBLIC_BASE_URL}/assets/{relative_path.as_posix()}"
        
        return public_url

    def _poll_until_complete(self, task_id: str) -> str:
        """Poll the operation status until video is ready."""
        url = f"{self.base_url}/api/v1/veo/record-info"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        for attempt in range(self.max_polls):
            logger.info(f"Polling Kie.ai Veo task (attempt {attempt + 1}/{self.max_polls})...")
            
            response = requests.get(url, headers=headers, params={"taskId": task_id}, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Poll returned {response.status_code}: {response.text}")
                time.sleep(self.poll_interval)
                continue
            
            data = response.json()
            
            if data.get("code") != 200:
                logger.warning(f"Poll error: {data.get('msg')}")
                time.sleep(self.poll_interval)
                continue
            
            task_data = data.get("data", {})
            success_flag = task_data.get("successFlag")
            
            # 0 = generating, 1 = success, 2/3 = failed
            if success_flag == 1:
                logger.info("Kie.ai Veo task completed!")
                logger.info(f"Response raw: {task_data}") # Debug log
                
                # Try to get resultUrls from 'response' object (as list)
                response_obj = task_data.get("response", {})
                if isinstance(response_obj, dict):
                    result_urls = response_obj.get("resultUrls", [])
                    if result_urls and isinstance(result_urls, list):
                        return result_urls[0]
                
                # Fallback: try parsing resultUrls as JSON string (old format)
                result_urls_str = task_data.get("resultUrls")
                if result_urls_str:
                    try:
                        result_urls = json.loads(result_urls_str)
                        if result_urls:
                            return result_urls[0]
                    except json.JSONDecodeError:
                        pass

                raise VideoGenerationError(f"No resultUrls in response: {task_data}")
            
            elif success_flag in [2, 3]:
                error_msg = task_data.get("msg", "Unknown error")
                raise VideoGenerationError(f"Kie.ai Veo task failed: {error_msg}")
            
            # Still generating (success_flag == 0)
            logger.info(f"Task generating (successFlag={success_flag})...")
            time.sleep(self.poll_interval)
        
        raise VideoGenerationError(f"Kie.ai Veo task timed out after {self.max_polls * self.poll_interval} seconds")

    def _download_video(self, video_url: str) -> str:
        """Download video from URL and return as data URI."""
        logger.info(f"Downloading video from: {video_url[:50]}...")
        
        response = requests.get(video_url, timeout=300, allow_redirects=True)
        
        if response.status_code != 200:
            raise VideoGenerationError(f"Failed to download video: {response.status_code}")
        
        # Return as data URI
        video_bytes = response.content
        video_b64 = base64.b64encode(video_bytes).decode("utf-8")
        
        logger.info(f"Video downloaded: {len(video_bytes)} bytes")
        
        return f"data:video/mp4;base64,{video_b64}"


# Alias for backward compatibility
VeoClient = KieVeoClient
