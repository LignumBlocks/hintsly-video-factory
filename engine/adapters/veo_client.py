class VeoClient:
    def generate(self, image_path: str, prompt: str) -> str:
        return f"https://mock-video-url.com/{prompt[:10].replace(' ', '_')}"
