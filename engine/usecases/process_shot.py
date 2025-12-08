from domain.entities import Shot
import traceback

class ProcessShot:
    def __init__(self, fs, prompt_service, image_client, video_client, logger):
        self.fs = fs
        self.prompt_service = prompt_service
        self.image_client = image_client
        self.video_client = video_client
        self.logger = logger

    def execute(self, shot: Shot) -> Shot:
        try:
            self.logger.info(f"Starting processing for shot {shot.video_id} block {shot.bloque} shot {shot.plano}")
            
            # 1. Generación de prompts
            if not shot.prompt_imagen:
                self.logger.info("Generating image prompt...")
                shot.prompt_imagen = self.prompt_service.generate_image_prompt(shot)

            if not shot.prompt_video:
                self.logger.info("Generating video prompt...")
                shot.prompt_video = self.prompt_service.generate_video_prompt(shot)

            # 2. Generar imagen
            self.logger.info(f"Generating image with prompt: {shot.prompt_imagen[:50]}...")
            img_url = self.image_client.generate(shot.prompt_imagen)
            shot.image_path = self.fs.save_image(shot, img_url)
            self.logger.info(f"Image saved to {shot.image_path}")

            # 3. Generar video
            self.logger.info(f"Generating video with prompt: {shot.prompt_video[:50]}...")
            vid_url = self.video_client.generate(shot.image_path, shot.prompt_video)
            shot.video_path = self.fs.save_video(shot, vid_url)
            self.logger.info(f"Video saved to {shot.video_path}")
            
            shot.estado = "COMPLETADO"
            
            # 4. Save metadata
            self.fs.save_metadata(shot)
            
        except Exception as e:
            shot.estado = "ERROR"
            shot.error_message = str(e)
            self.logger.error(f"Error processing shot: {e}")
            self.logger.error(traceback.format_exc())
            # Save metadata allows debugging even on error
            try:
                self.fs.save_metadata(shot)
            except:
                pass 
        
        return shot
