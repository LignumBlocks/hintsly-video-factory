from unittest.mock import MagicMock, patch

from domain.nanobanana_models import NanoBananaRequest, NanoBananaProject, NanoBananaImageTask, NanoBananaOutputConfig, NanoBananaProductionRules, NanoBananaApproval
from usecases.run_nanobanana_generation import RunNanoBananaGeneration
from adapters.logger import Logger
from adapters.assets_repository import Asset

# Mocks
mock_repo = MagicMock()
mock_prompt_service = MagicMock()
mock_client = MagicMock()
mock_assets_repo = MagicMock()
mock_logger = MagicMock(spec=Logger)

def create_mock_request():
    return NanoBananaRequest(
        project=NanoBananaProject(
            project_id="p1", 
            title="T", 
            scope_blocks_included=[], 
            output=NanoBananaOutputConfig(aspect_ratio="16:9", resolution_px="1K", image_format="png"), 
            production_rules=NanoBananaProductionRules(nanobanana_max_reference_images=5, nanobanana_variants_per_image_task=1, approval_gate="none")
        ),
        asset_library={},
        image_tasks=[
            NanoBananaImageTask(task_id="t1", block_id="b", shot_id="s", role="r", refs=["ref1"], prompt="p", approval=NanoBananaApproval(status="PENDING_REVIEW"))
        ]
    )

def test_execution_flow():
    # Setup Mocks
    mock_repo.get.return_value = create_mock_request()
    
    mock_prompt_service.construct_prompt.return_value = "Constructed Prompt"
    mock_prompt_service.construct_negative_prompt.return_value = "Constructed Negative"
    
    # Asset Resolution Mock
    mock_assets_repo.get_asset.return_value = Asset(asset_id="ref1", file_name="ref1", tipo_asset="img", mv_context_default="", descripcion_visual="", uso_sugerido="")
    mock_assets_repo.resolve_file_path.return_value = "/home/roiky/valid/path/assets/ref1.png"
    
    # Client Mock (Success)
    mock_client.generate_image.return_value = ["http://result.url/img.png"]

    # Use Case
    # Note: mocking public_base_url via Config might be hard without patching, but the class reads it from Config.PUBLIC_BASE_URL.
    # We can patch os.path.relpath to ensure stable URL generation for test if needed, or check logic.
    
    with patch("usecases.run_nanobanana_generation.Config") as MockConfig:
        MockConfig.PUBLIC_BASE_URL = "http://test.com"
        # We need to ensure ASSETS_DIR logic works. 
        # Alternatively, we just mock _resolve_refs_to_urls if we want to test execution flow distinct from URL logic.
        # But let's test it all together.
        
        # Patch os.path.relpath because our mock path might not be relative to real ASSETS_DIR
        with patch("os.path.relpath") as mock_relpath:
             mock_relpath.return_value = "ref1.png"
             
             use_case = RunNanoBananaGeneration(mock_repo, mock_prompt_service, mock_client, mock_assets_repo, mock_logger)
             use_case.public_base_url = "http://test.com" # Override manually
             
             results = use_case.execute("p1")
             
             # Verify
             assert "t1" in results
             assert results["t1"] == ["http://result.url/img.png"]
             
             # Check Client Call
             mock_client.generate_image.assert_called_once()
             call_args = mock_client.generate_image.call_args[1]
             assert call_args["prompt"] == "Constructed Prompt"
             assert call_args["negative_prompt"] == "Constructed Negative"
             assert call_args["reference_images"] == ["http://test.com/assets/ref1.png"]
             
             print("test_execution_flow: PASSED")

def test_execution_dry_run():
    mock_repo.get.return_value = create_mock_request()
    use_case = RunNanoBananaGeneration(mock_repo, mock_prompt_service, mock_client, mock_assets_repo, mock_logger)
    
    mock_client.reset_mock()
    results = use_case.execute("p1", dry_run=True)
    
    assert "t1" in results
    mock_client.generate_image.assert_not_called()
    print("test_execution_dry_run: PASSED")

if __name__ == "__main__":
    try:
        test_execution_flow()
        test_execution_dry_run()
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
