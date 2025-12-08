from domain.entities import Shot

# Global style definition for consistency
IMAGE_STYLE = "cinematic, photorealistic, 8k, highly detailed, dramatic lighting, movie still"
VIDEO_STYLE = "high quality, stable, 4k, cinematic motion, smooth transition"

class PromptService:
    def generate_image_prompt(self, shot: Shot) -> str:
        """
        Generates a refined image prompt by combining the visual description
        with a predefined cinematic style.
        """
        visual_desc = shot.descripcion_visual.strip().rstrip(".")
        
        # Combine visual description with style keywords
        prompt = f"{visual_desc}. {IMAGE_STYLE}"
        return prompt

    def generate_video_prompt(self, shot: Shot) -> str:
        """
        Generates a video generation prompt focusing on movement and quality.
        """
        visual_desc = shot.descripcion_visual.strip().rstrip(".")
        movement = shot.movimiento_camara.strip()
        
        # Construct video prompt
        # Priority: Movement instruction + Subject context + Quality boosters
        prompt = f"{movement} of {visual_desc}. {VIDEO_STYLE}"
        return prompt
