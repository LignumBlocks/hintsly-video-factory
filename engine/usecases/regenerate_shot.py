from engine.domain.entities import Shot

class RegenerateShot:
    def __init__(self, process_shot):
        self.process_shot = process_shot

    def execute(self, shot: Shot) -> Shot:
        shot.prompt_imagen = None
        shot.prompt_video = None
        shot.image_path = None
        shot.video_path = None
        return self.process_shot.execute(shot)
