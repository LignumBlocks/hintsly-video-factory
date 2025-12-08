class GeminiClient:
    def generate(self, prompt: str) -> str:
        return f"https://mock-image-url.com/{prompt[:10].replace(' ', '_')}"
