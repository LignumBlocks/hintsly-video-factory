import os
import json
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
from domain.nanobanana_models import NanoBananaRequest
from adapters.nanobanana_repository import NanoBananaRepository
from adapters.nanobanana_client import NanoBananaClient
from adapters.assets_repository import AssetsRepository
from adapters.logger import Logger
from usecases.nanobanana_prompt_service import NanoBananaPromptService
from usecases.run_nanobanana_generation import RunNanoBananaGeneration
from infra.paths import ASSETS_DIR
from infra.config import Config

# --- CONFIGURATION ---
JSON_PATH = "assets/catalog_files/NanoBananaPro.json"
TARGET_TASK_ID = "img__csj__B01__P01__start"  # Change this to run a different task

def run_diagnostic():
    print("=== NANO BANANA PRO: SINGLE TASK DIAGNOSTIC ===")
    
    # 1. Setup Detailed Logging
    # We use both the custom Logger and standard logging to catch everything
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = Logger()
    
    # 2. Initialize Components
    print(f"[*] Initializing components...")
    assets_repo = AssetsRepository(files_dir=Config.ASSETS_FILES_DIR)
    banana_repo = NanoBananaRepository()
    prompt_service = NanoBananaPromptService()
    client = NanoBananaClient()
    use_case = RunNanoBananaGeneration(banana_repo, prompt_service, client, assets_repo, logger)

    # 3. Load Project Data
    if not os.path.exists(JSON_PATH):
        print(f"[!] Error: {JSON_PATH} not found.")
        return

    print(f"[*] Loading JSON: {JSON_PATH}")
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)
    
    request_model = NanoBananaRequest(**data)
    
    # 4. Filter for Target Task
    print(f"[*] Searching for Task: {TARGET_TASK_ID}")
    target_tasks = [t for t in request_model.image_tasks if t.task_id == TARGET_TASK_ID]
    
    if not target_tasks:
        print(f"[!] Task {TARGET_TASK_ID} not found in JSON.")
        available_ids = [t.task_id for t in request_model.image_tasks[:5]]
        print(f"    Available (first 5): {available_ids}")
        return
    
    task = target_tasks[0]
    request_model.image_tasks = [task] # Isolate this task for the use case
    banana_repo.save(request_model)

    print(f"--- TASK DATA ---")
    print(f"ID: {task.task_id}")
    print(f"Refs: {task.refs}")
    print(f"Prompt: {task.prompt}")
    print(f"-----------------")

    # 5. Pre-execution Check: Resolution
    print(f"[*] Resolving Assets...")
    urls = use_case._resolve_refs_to_urls(task.refs)
    for i, u in enumerate(urls):
        print(f"  Ref {i+1}: {u}")

    # 6. Pre-execution Check: Prompt
    final_p = prompt_service.construct_prompt(request_model.style_presets, task)
    final_n = prompt_service.construct_negative_prompt(request_model.style_presets, task)
    print(f"[*] Constructed Prompt: {final_p[:100]}...")
    print(f"[*] Constructed Negative: {final_n[:100]}...")

    # Pre-compute project_id and task_id for use in execution and logging
    project_id = request_model.project.project_id
    task_id = task.task_id

    # 7. EXECUTE
    print("\n>>> STARTING GENERATION (Real API Call) <<<")
    try:
        results = use_case.execute(project_id, dry_run=False)
        
        print("\n=== EXECUTION RESULTS ===")
        total_images = sum(len(files) for files in results.values())
        if total_images > 0:
            print(f"[SUCCESS] {total_images} image(s) generated.")
            for tid, files in results.items():
                for f in files:
                    print(f"  -> Path: {f}")
                    if not f.startswith("http"):
                        if os.path.exists(f):
                            print("     [FILE VERIFIED ON DISK]")
                        else:
                            print("     [ERROR: FILE NOT FOUND ON DISK]")
        else:
            print("[FAILURE] No images were generated.")

        # Save JSON log
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id,
            "task_id": task_id,
            "results": results
        }
        # Ensure the directory for the log file exists
        log_dir = os.path.dirname("engine/diagnostic_log.json")
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        with open("engine/diagnostic_log.json", "w") as f:
            json.dump(log_data, f, indent=2)
        print(f"\n[*] Diagnostic log saved to: engine/diagnostic_log.json")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_diagnostic()
