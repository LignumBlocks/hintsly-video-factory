from domain.entities import Shot

class PromptService:
    def generate_image_prompt(self, shot: Shot) -> str:
        return f"Image of {shot.descripcion_visual}, style: cinematic"

    def generate_video_prompt(self, shot: Shot) -> str:
        return f"Video of {shot.descripcion_visual}, movement: {shot.movimiento_camara}"
