import os
import shutil
from pathlib import Path
from domain.entities import Shot
from infra.paths import ASSETS_DIR

class FSAdapter:
    def _get_shot_dir(self, shot: Shot) -> Path:
        return ASSETS_DIR / "videos" / shot.video_id / f"block_{shot.bloque}" / f"shot_{shot.plano}"

    def save_image(self, shot: Shot, img_data: str) -> str:
        # img_data is a URL or dummy string for now
        shot_dir = self._get_shot_dir(shot)
        os.makedirs(shot_dir, exist_ok=True)
        file_path = shot_dir / "image.png"
        
        # For now, just write the dummy data to a file
        with open(file_path, "w") as f:
            f.write(f"Image data from {img_data}")
            
        return str(file_path)

    def save_video(self, shot: Shot, vid_data: str) -> str:
        shot_dir = self._get_shot_dir(shot)
        os.makedirs(shot_dir, exist_ok=True)
        file_path = shot_dir / "video.mp4"
        
        with open(file_path, "w") as f:
            f.write(f"Video data from {vid_data}")
            
        return str(file_path)
