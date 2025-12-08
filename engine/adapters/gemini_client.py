import time
import requests
from adapters.logger import Logger
from domain.errors import ImageGenerationError, PromptError
from infra.config import Config

logger = Logger()

class KieNanoBananaClient:
    """
    Client for Kie.ai Nano Banana API (google/nano-banana-pro).
    Uses async task-based API with polling.
    """
    
    def __init__(self):
        self.api_key = Config.KIE_API_KEY
        self.base_url = Config.KIE_API_BASE
        self.model = Config.KIE_NANO_BANANA_MODEL
        self.poll_interval = 3  # seconds
        self.max_polls = 60  # max ~3 minutes
        
        if not self.api_key:
            logger.warning("KIE_API_KEY not found in environment variables.")

    def generate(self, prompt: str) -> str:
        """
        Generate an image using Kie.ai Nano Banana API.
        
        Args:
            prompt: Text prompt for image generation
            
        Returns:
            URL of the generated image
        """
        if not self.api_key:
            raise ImageGenerationError("KIE_API_KEY is missing")

        if not prompt:
            raise PromptError("Prompt cannot be empty")

        try:
            # Step 1: Create task
            task_id = self._create_task(prompt)
            
            # Step 2: Poll until completion
            image_url = self._poll_until_complete(task_id)
            
            # Step 3: Download and return as data URI
            return self._download_image(image_url)

        except ImageGenerationError:
            raise
        except Exception as e:
            logger.error(f"Kie.ai Nano Banana generation failed: {e}")
            raise ImageGenerationError(f"Image generation failed: {e}")

    def _create_task(self, prompt: str) -> str:
        """Submit image generation task to Kie.ai API."""
        url = f"{self.base_url}/api/v1/jobs/createTask"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "prompt": prompt,
                "output_format": "png",
                "image_size": "1:1"
            }
        }
        
        logger.info(f"Submitting Kie.ai task with prompt: {prompt[:50]}...")
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Payload: {payload}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response text: {response.text}")
        
        if response.status_code != 200:
            error_msg = response.text
            logger.error(f"Kie.ai API error: {error_msg}")
            raise ImageGenerationError(f"Kie.ai API returned {response.status_code}: {error_msg}")
        
        data = response.json()
        
        if data.get("code") != 200:
            raise ImageGenerationError(f"Kie.ai error: {data.get('msg')}")
        
        task_id = data.get("data", {}).get("taskId")
        
        if not task_id:
            raise ImageGenerationError(f"No taskId in response: {data}")
        
        logger.info(f"Kie.ai task created: {task_id}")
        return task_id

    def _poll_until_complete(self, task_id: str) -> str:
        """Poll task status until image is ready."""
        url = f"{self.base_url}/api/v1/jobs/recordInfo"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        for attempt in range(self.max_polls):
            logger.info(f"Polling Kie.ai task (attempt {attempt + 1}/{self.max_polls})...")
            
            response = requests.get(url, headers=headers, params={"taskId": task_id}, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Poll returned {response.status_code}: {response.text}")
                time.sleep(self.poll_interval)
                continue
            
            data = response.json()
            
            if data.get("code") != 200:
                logger.warning(f"Poll error: {data.get('message')}")
                time.sleep(self.poll_interval)
                continue
            
            task_data = data.get("data", {})
            state = task_data.get("state")
            
            # States: waiting, queuing, generating, success, fail
            if state == "success":
                logger.info("Kie.ai task completed!")
                
                # Parse resultJson which contains resultUrls
                result_json_str = task_data.get("resultJson", "{}")
                import json
                result_obj = json.loads(result_json_str)
                
                result_urls = result_obj.get("resultUrls", [])
                if result_urls:
                    return result_urls[0]
                
                raise ImageGenerationError(f"No resultUrls in response: {result_obj}")
            
            elif state == "fail":
                fail_code = task_data.get("failCode", "")
                fail_msg = task_data.get("failMsg", "Unknown error")
                raise ImageGenerationError(f"Kie.ai task failed [{fail_code}]: {fail_msg}")
            
            # Still processing (waiting, queuing, generating)
            logger.info(f"Task state: {state}")
            time.sleep(self.poll_interval)
        
        raise ImageGenerationError(f"Kie.ai task timed out after {self.max_polls * self.poll_interval} seconds")

    def _download_image(self, image_url: str) -> str:
        """Download image and return as data URI."""
        import base64
        
        logger.info(f"Downloading image from: {image_url[:50]}...")
        
        response = requests.get(image_url, timeout=60)
        
        if response.status_code != 200:
            raise ImageGenerationError(f"Failed to download image: {response.status_code}")
        
        # Determine mime type from content-type header or default to png
        content_type = response.headers.get("Content-Type", "image/png")
        if "jpeg" in content_type or "jpg" in content_type:
            mime_type = "image/jpeg"
        elif "webp" in content_type:
            mime_type = "image/webp"
        else:
            mime_type = "image/png"
        
        image_bytes = response.content
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        
        logger.info(f"Image downloaded: {len(image_bytes)} bytes")
        
        return f"data:{mime_type};base64,{image_b64}"


# Alias for backward compatibility
GeminiImageClient = KieNanoBananaClient
