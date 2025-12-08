from domain.entities import Shot

class ProcessShot:
    def __init__(self, fs, prompt_service, image_client, video_client):
        self.fs = fs
        self.prompt_service = prompt_service
        self.image_client = image_client
        self.video_client = video_client

    def execute(self, shot: Shot) -> Shot:
        # 1. Generación de prompts
        if not shot.prompt_imagen:
            shot.prompt_imagen = self.prompt_service.generate_image_prompt(shot)

        if not shot.prompt_video:
            shot.prompt_video = self.prompt_service.generate_video_prompt(shot)

        # 2. Generar imagen
        img_url = self.image_client.generate(shot.prompt_imagen)
        shot.image_path = self.fs.save_image(shot, img_url)

        # 3. Generar video
        vid_url = self.video_client.generate(shot.image_path, shot.prompt_video)
        shot.video_path = self.fs.save_video(shot, vid_url)

        shot.estado = "COMPLETADO"
        return shot
