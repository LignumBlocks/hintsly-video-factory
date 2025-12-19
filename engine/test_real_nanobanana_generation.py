import os
import sys
import json
import httpx
from datetime import datetime

# Add engine to path
sys.path.append(os.getcwd())

from domain.nanobanana_models import NanoBananaRequest, NanoBananaImageTask
from adapters.nanobanana_client import NanoBananaClient
from adapters.assets_repository import AssetsRepository
from adapters.nanobanana_repository import NanoBananaRepository
from usecases.nanobanana_prompt_service import NanoBananaPromptService
from usecases.run_nanobanana_generation import RunNanoBananaGeneration
from adapters.logger import Logger
from infra.config import Config

# Setup output dir
OUTPUT_DIR = "test_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

logger = Logger()

def test_real_generation():
    print(f"--- Starting REAL NanoBanana Generation Test ---")
    print(f"Output Directory: {OUTPUT_DIR}")
    
    # 1. Initialize Components
    print("Initializing components...")
    assets_repo = AssetsRepository(files_dir=Config.ASSETS_FILES_DIR)
    banana_repo = NanoBananaRepository()
    client = NanoBananaClient() # Uses env vars
    prompt_service = NanoBananaPromptService()
    
    use_case = RunNanoBananaGeneration(banana_repo, prompt_service, client, assets_repo, logger)
    
    # 2. Ingest Data (Simulate Ingest)
    print("Ingesting NanoBananaPro.json...")
    json_path = "assets/catalog_files/NanoBananaPro.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    request_model = NanoBananaRequest(**data)
    banana_repo.save(request_model)
    
    # 3. Pick ONE Task (The first one)
    task = request_model.image_tasks[0]
    print(f"Selected Task: {task.task_id}")
    print(f"Prompt: {task.prompt[:50]}...")
    
    # 4. Construct Inputs (Manually calling use case steps to inspect/save metadata)
    # We could call use_case.execute() but we want to intercept just one task and save metadata.
    # Let's reuse logic from use_case helpers where possible or recreate for this test script.
    
    global_style = request_model.style_presets
    final_prompt = prompt_service.construct_prompt(global_style, task)
    final_negative = prompt_service.construct_negative_prompt(global_style, task)
    
    ref_urls = use_case._resolve_refs_to_urls(task.refs)
    
    print(f"Resolved {len(ref_urls)} Validation Refs (Public URLs):")
    for u in ref_urls:
        print(f" - {u}")
        
    # 5. Execute Generation via Use Case (Verification of IMG-07)
    print(">>> CALLING USE CASE (this may take time)...")
    
    # We execute for the whole project, or we can mock/filter.
    # The use case processes ALL tasks. In our test file we have multiple tasks?
    # NanoBananaPro.txt has many tasks. We might want to just process the first one to save credits/time?
    # The Use Case currently loops all.
    # Let's filter the request in the repo to only have 1 task for this test.
    
    # Mock the client generation to avoid timeouts and verify persistence logic (IMG-07)
    # We use a placeholder image that is guaranteed to be downloadable.
    client.generate_image = lambda **kwargs: ["https://placehold.co/600x400/png"]
    
    try:
        results = use_case.execute(request_model.project.project_id)
        print("Use Case Execution Successful!")
        print("Results:", json.dumps(results, indent=2))
        
        # Verify files exist
        task_result = results.get(task.task_id)
        if isinstance(task_result, list):
            for path in task_result:
                if os.path.exists(path):
                    print(f"VERIFIED: File exists at {path}")
                else:
                    print(f"FAILED: File missing at {path}")
        else:
             print(f"FAILED: Result is not a list of paths: {task_result}")
             
    except Exception as e:
        print(f"Use Case Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_generation()
