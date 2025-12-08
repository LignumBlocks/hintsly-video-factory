from fastapi import FastAPI
from engine.domain.entities import Shot
from engine.usecases.process_shot import ProcessShot
from engine.usecases.regenerate_shot import RegenerateShot
from engine.usecases.utils_prompt import PromptService
from engine.adapters.fs_adapter import FSAdapter
from engine.adapters.gemini_client import GeminiClient
from engine.adapters.veo_client import VeoClient
from engine.adapters.logger import Logger

app = FastAPI()

# Instantiate adapters (mocks for now)
fs_adapter = FSAdapter()
prompt_service = PromptService()
gemini_client = GeminiClient()
veo_client = VeoClient()
logger = Logger()

# Instantiate use cases
process_shot_usecase = ProcessShot(fs_adapter, prompt_service, gemini_client, veo_client)
regenerate_shot_usecase = RegenerateShot(process_shot_usecase)

@app.post("/shots/process")
def process_shot(shot: Shot):
    return process_shot_usecase.execute(shot)

@app.post("/shots/regenerate")
def regenerate_shot(shot: Shot):
    return regenerate_shot_usecase.execute(shot)
