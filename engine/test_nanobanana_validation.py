from domain.nanobanana_models import NanoBananaImageTask, NanoBananaRequest, NanoBananaProject, NanoBananaProductionRules, NanoBananaOutputConfig
from pydantic import ValidationError

def create_mock_request(tasks):
    return NanoBananaRequest(
        project=NanoBananaProject(
            project_id="test_proj",
            title="Test",
            scope_blocks_included=[],
            output=NanoBananaOutputConfig(aspect_ratio="16:9", resolution_px=[1920, 1080], image_format="png"),
            production_rules=NanoBananaProductionRules(nanobanana_max_reference_images=8, nanobanana_variants_per_image_task=1, approval_gate="false")
        ),
        asset_library={},
        image_tasks=tasks
    )

def test_unique_task_ids():
    tasks = [
        NanoBananaImageTask(task_id="t1", block_id="b1", shot_id="s1", role="start", refs=[], prompt="p", approval={"status": "OK"}),
        NanoBananaImageTask(task_id="t2", block_id="b1", shot_id="s2", role="start", refs=[], prompt="p", approval={"status": "OK"})
    ]
    req = create_mock_request(tasks)
    assert len(req.image_tasks) == 2

def test_duplicate_task_ids_raises_error():
    tasks = [
        NanoBananaImageTask(task_id="t1", block_id="b1", shot_id="s1", role="start", refs=[], prompt="p", approval={"status": "OK"}),
        NanoBananaImageTask(task_id="t1", block_id="b1", shot_id="s2", role="start", refs=[], prompt="p", approval={"status": "OK"})
    ]
    try:
        create_mock_request(tasks)
        raise AssertionError("Should have raised ValidationError for duplicate task_ids")
    except ValidationError as e:
        print(f"Caught expected error: {e}")
        assert "Duplicate task_ids found" in str(e)

if __name__ == "__main__":
    # Minimal manual runner if pytest not available/configured
    try:
        test_unique_task_ids()
        print("test_unique_task_ids: PASSED")
        test_duplicate_task_ids_raises_error()
        print("test_duplicate_task_ids_raises_error: PASSED")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
