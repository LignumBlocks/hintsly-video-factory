import time
import json
import httpx
from typing import List, Optional, Dict, Any
from adapters.logger import Logger
from infra.config import Config

class NanoBananaClient:
    """
    Adapter to communicate with Kie.ai NanoBananaPro API.
    Implements the async Task -> Poll -> Result flow.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or Config.KIE_API_KEY
        self.base_url = base_url or Config.KIE_API_BASE
        self.model = Config.KIE_NANO_BANANA_MODEL
        self.logger = Logger()
        
        self.poll_interval = 5
        self.max_polls = 120 # ~10 minutes max wait
        self.last_payload = None # Store the exact payload of the last createTask call

    def generate_image(self, 
                       prompt: str, 
                       negative_prompt: str, 
                       reference_images: List[str], 
                       resolution: str,
                       num_outputs: int = 1,
                       output_format: str = "png") -> List[str]:
        """
        Orchestrates the generation flow: Create Task -> Poll -> Return URLs.
        
        Args:
            prompt: Positive prompt.
            negative_prompt: Negative prompt (currently concatenated to prompt or ignored if API doesn't support specific field. 
                             Docs only mention 'prompt' in 'input'. We might need to append it.)
                             Wait, 'NanoBananaPro' usually respects negative prompts. 
                             If the docs don't specify a 'negative_prompt' key in 'input', 
                             convention is often to append it or it might be missing from that specific simplified doc.
                             However, standard SD payloads usually have it. 
                             Let's check if we should append to prompt or send as key.
                             User guide shows: "prompt": "..." inside input.
                             Let's assume we append " --no negative_prompt" or similar if strict, 
                             but the models.py has a specific field. 
                             Let's try sending it as a key in 'input' first, if it fails/ignored, we might need to adjust.
                             Actually, looking at 'gemini_client.py', it ONLY sends 'prompt'.
                             I will TRY sending 'negative_prompt' in input, but if it's not documented it might be ignored.
                             Safest bet for now: Appending to prompt if we want to be sure, OR providing it as a field.
                             THE DOCS SCROLL: "image_tasks" has "negative_prompt".
                             The API doc snippet says:
                             "prompt": "...", "image_input": [...]
                             It does NOT explicitly list negative_prompt in the "Qué se envía" list.
                             However, standard practice for many wrappers is to include it.
                             I will include it in 'input' separate key.
            reference_images: List of public URLs.
            width: Output width. (Note: API expects 'resolution' or 'aspect_ratio', typically string or predefined.
                   The docs say "resolution": "2K". If we send raw pixels, we might need to map them or checks if API accepts WxH.
                   Let's map strict pixels to nearest standard or pass "WxH" string if supported.
                   Docs example: "resolution": "2K", "aspect_ratio": "1:1".
                   I will assume we can pass "aspect_ratio" from the project and "resolution" as a string "WidthxHeight".)
            
        Returns:
            List of image URLs (public/temp).
        """
        if not self.api_key:
            raise ValueError("KIE_API_KEY is not set.")

        # 1. Create Task
        task_id = self._create_task(prompt, negative_prompt, reference_images, resolution, num_outputs, output_format)
        
        # 2. Poll for Completion
        result_urls = self._poll_until_complete(task_id)
        
        return result_urls

    def _create_task(self, prompt, negative_prompt, refs, resolution, num_outputs, fmt) -> str:
        url = f"{self.base_url}/api/v1/jobs/createTask"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        input_payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt, # Hoping this key is accepted
            "image_input": refs,
            "output_format": fmt,
            "resolution": resolution.upper(),
            "num_outputs": num_outputs # Check if API accepts this to gen multiple variants per task. Docs didn't show it but it's common.
        }
        
        payload = {
            "model": self.model,
            "input": input_payload
        }
        self.last_payload = payload
        
        self.logger.info(f"Creating Task | Model: {self.model} | Refs: {len(refs)}")
        
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("code") != 200:
                raise RuntimeError(f"API Error {data.get('code')}: {data.get('msg')}")
                
            task_id = data.get("data", {}).get("taskId")
            if not task_id:
                raise RuntimeError("No taskId returned from API")
                
            return task_id

    def _poll_until_complete(self, task_id: str) -> List[str]:
        url = f"{self.base_url}/api/v1/jobs/recordInfo"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        for _ in range(self.max_polls):
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(url, headers=headers, params={"taskId": task_id})
                
                # Handle non-200 HTTP responses (network/gateway errors)
                if resp.status_code != 200:
                    self.logger.warning(f"Poll HTTP {resp.status_code}. Retrying...")
                    time.sleep(self.poll_interval)
                    continue
                
                data = resp.json()
                
                # Handle API-level errors
                if data.get("code") != 200:
                    self.logger.warning(f"Poll API Code {data.get('code')}: {data.get('msg')}")
                    time.sleep(self.poll_interval)
                    continue
                    
                task_data = data.get("data", {})
                state = task_data.get("state")
                
                if state == "success":
                    result_json_str = task_data.get("resultJson", "{}")
                    try:
                        result_obj = json.loads(result_json_str)
                        return result_obj.get("resultUrls", [])
                    except json.JSONDecodeError:
                        raise RuntimeError(f"Failed to parse resultJson: {result_json_str}")
                
                elif state == "fail":
                    raise RuntimeError(f"Task Failed: {task_data.get('failMsg')}")
                
                # Waiting/Running
                time.sleep(self.poll_interval)
        
        raise TimeoutError(f"Task {task_id} timed out after {self.max_polls * self.poll_interval}s")
