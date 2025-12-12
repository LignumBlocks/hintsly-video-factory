from domain.entities import Shot, Asset
from typing import Optional

# Global style definition for consistency
IMAGE_STYLE = "cinematic, photorealistic, 8k, highly detailed, dramatic lighting, movie still"
VIDEO_STYLE = "high quality, stable, 4k, cinematic motion, smooth transition"

class PromptService:
    def generate_image_prompt(self, shot: Shot, asset: Optional[Asset] = None) -> str:
        """
        Generates image prompt using V2 semantic fields.
        Incorporates mv_context, funcion_narrativa, and descripcion_visual.
        If 'asset' is provided, adds a Visual Anchor to the prompt.
        """
        visual_desc = shot.descripcion_visual.strip().rstrip(".")
        
        # Build context prefix from mv_context
        # Map common mv_context values to style prefixes
        context_map = {
            "REAL_CHAOS": "In a chaotic, realistic documentary style",
            "CINEMATIC": "In a cinematic, dramatic style",
            "MINIMALIST": "In a minimalist, clean style",
            "VINTAGE": "In a vintage, nostalgic style",
        }
        context_prefix = context_map.get(shot.mv_context, f"In a {shot.mv_context.lower().replace('_', ' ')} style")
        
        # Add Asset Anchor if present
        asset_anchor = ""
        if asset:
             asset_anchor = f" Visual Anchor: {asset.descripcion_visual}."
        
        # Combine: context + visual + narrative function + style + anchor
        prompt = f"{context_prefix}, {visual_desc}. {shot.funcion_narrativa}.{asset_anchor} {IMAGE_STYLE}"
        return prompt

    def generate_video_prompt(self, shot: Shot) -> str:
        """
        Generates video prompt with camera movement and duration context.
        Uses V2 fields: camera_move, duracion_seg, descripcion_visual.
        """
        visual_desc = shot.descripcion_visual.strip().rstrip(".")
        movement = shot.camera_move.strip()
        duration = shot.duracion_seg
        
        # Include duration hint for motion pacing
        prompt = f"{movement} of {visual_desc}, {duration} seconds duration. {VIDEO_STYLE}"
        return prompt
