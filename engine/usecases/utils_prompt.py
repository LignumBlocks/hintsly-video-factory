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
            "REAL_CHAOS": "In a realistic, raw, slightly chaotic everyday environment (REAL_CHAOS)",
            "LAB_WIDE": "Wide shot of the high-tech Financial War Room (LAB_WIDE)",
            "LAB_TABLE": "Close-up on the central holographic command table (LAB_TABLE)",
            "DATA_PANEL": "Focus on a digital data interface or screen element (DATA_PANEL)",
            "CINEMATIC": "In a cinematic, dramatic style",
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
        raw_move = shot.camera_move.strip().lower()
        duration = shot.duracion_seg
        
        move_map = {
            "static": "Static camera",
            "zoom_in": "Slow zoom in",
            "zoom_out": "Slow zoom out",
            "dolly_in": "Smooth dolly in",
            "dolly_out": "Smooth dolly out",
            "orbit_left": "Orbiting left", 
            "orbit_right": "Orbiting right",
            "pan_left": "Panning left",
            "pan_right": "Panning right",
            "tilt_up": "Tilting up",
            "tilt_down": "Tilting down",
            "handheld_subtle": "Subtle handheld camera movement"
        }
        
        movement = move_map.get(raw_move, raw_move)
        
        # Include duration hint for motion pacing
        prompt = f"{movement} of {visual_desc}, {duration} seconds duration. {VIDEO_STYLE}"
        return prompt
