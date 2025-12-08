from fastapi import FastAPI
from domain.entities import Shot
from usecases.process_shot import ProcessShot
from usecases.regenerate_shot import RegenerateShot
from usecases.utils_prompt import PromptService
from adapters.fs_adapter import FSAdapter
from adapters.gemini_client import GeminiImageClient
from adapters.veo_client import VeoClient
from adapters.logger import Logger

app = FastAPI()

# Instantiate adapters
fs_adapter = FSAdapter()
prompt_service = PromptService()
gemini_client = GeminiImageClient()
veo_client = VeoClient()
logger = Logger()

# Instantiate use cases
process_shot_usecase = ProcessShot(fs_adapter, prompt_service, gemini_client, veo_client, logger)
regenerate_shot_usecase = RegenerateShot(process_shot_usecase)

@app.post("/shots/process")
def process_shot(shot: Shot):
    return process_shot_usecase.execute(shot)

@app.post("/shots/regenerate")
def regenerate_shot(shot: Shot):
    return regenerate_shot_usecase.execute(shot)
