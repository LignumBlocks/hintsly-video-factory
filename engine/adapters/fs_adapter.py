import os
import shutil
import base64
import requests
from pathlib import Path
from domain.entities import Shot
from infra.paths import ASSETS_DIR

class FSAdapter:
    def _get_shot_dir(self, shot: Shot) -> Path:
        return ASSETS_DIR / "videos" / shot.video_id / f"block_{shot.bloque}" / f"shot_{shot.plano}"

    def save_image(self, shot: Shot, img_data: str) -> str:
        shot_dir = self._get_shot_dir(shot)
        os.makedirs(shot_dir, exist_ok=True)
        
        # Handle Base64 Data URI
        if img_data.startswith("data:"):
            try:
                header, encoded = img_data.split(",", 1)
                # Determine extension based on mime type in header
                ext = ".png"
                if "image/jpeg" in header:
                    ext = ".jpg"
                elif "image/webp" in header:
                    ext = ".webp"
                
                file_path = shot_dir / f"image{ext}"
                
                data = base64.b64decode(encoded)
                with open(file_path, "wb") as f:
                    f.write(data)
                return str(file_path)
            except Exception as e:
                print(f"Error saving base64 image: {e}")
                file_path = shot_dir / "image_error.txt"
                with open(file_path, "w") as f:
                    f.write(f"Failed to decode: {str(e)}\n\nData: {img_data[:100]}...")
                return str(file_path)
                
        else:
            # Fallback for URLs or raw data
            file_path = shot_dir / "image.png"
            with open(file_path, "w") as f:
                f.write(f"Image data from {img_data}")
            
        return str(file_path)

    def save_video(self, shot: Shot, vid_data: str) -> str:
        shot_dir = self._get_shot_dir(shot)
        os.makedirs(shot_dir, exist_ok=True)
        file_path = shot_dir / "video.mp4"
        
        # Handle Base64 Data URI (from Veo client)
        if vid_data.startswith("data:"):
            try:
                header, encoded = vid_data.split(",", 1)
                data = base64.b64decode(encoded)
                with open(file_path, "wb") as f:
                    f.write(data)
                print(f"Video saved from base64: {len(data)} bytes")
                return str(file_path)
            except Exception as e:
                print(f"Error saving base64 video: {e}")
                error_path = shot_dir / "video_error.txt"
                with open(error_path, "w") as f:
                    f.write(f"Failed to decode video: {str(e)}")
                return str(error_path)
        
        # Check if it's a mock URL
        elif "mock" in vid_data:
             with open(file_path, "w") as f:
                 f.write(f"Simulated video content from {vid_data}")
        else:
             # Try real download from URL
             try:
                 print(f"Downloading video from {vid_data}...")
                 with requests.get(vid_data, stream=True, timeout=120) as r:
                     r.raise_for_status()
                     with open(file_path, 'wb') as f:
                         for chunk in r.iter_content(chunk_size=8192): 
                             f.write(chunk)
             except Exception as e:
                 print(f"Failed to download video: {e}")
                 with open(file_path, "w") as f:
                     f.write(f"Failed to download video from {vid_data}. Error: {e}")
            
        return str(file_path)

    def save_metadata(self, shot: Shot) -> str:
        shot_dir = self._get_shot_dir(shot)
        os.makedirs(shot_dir, exist_ok=True)
        file_path = shot_dir / "metadata.json"
        
        import json
        # Use .dict() for Pydantic v1 or .model_dump() for v2
        # Assuming v1 or compatible v2 for simplicity
        try:
            data = shot.model_dump()
        except AttributeError:
            data = shot.dict()
            
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
            
        return str(file_path)
