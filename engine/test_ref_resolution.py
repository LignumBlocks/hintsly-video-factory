from domain.nanobanana_models import NanoBananaRequest, NanoBananaProject, NanoBananaProductionRules, NanoBananaOutputConfig, NanoBananaImageTask, NanoBananaApproval
from adapters.assets_repository import AssetsRepository, Asset
from usecases.ingest_nanobanana import IngestNanoBanana
from adapters.logger import Logger
from unittest.mock import MagicMock

# Mock Logger
mock_logger = MagicMock(spec=Logger)

# Mock AssetsRepository
mock_repo = MagicMock(spec=AssetsRepository)

def create_mock_request(refs, max_refs=5):
    return NanoBananaRequest(
        project=NanoBananaProject(
            project_id="test_proj",
            title="Test",
            scope_blocks_included=[],
            output=NanoBananaOutputConfig(aspect_ratio="16:9", resolution_px=[1920, 1080], image_format="png"),
            production_rules=NanoBananaProductionRules(nanobanana_max_reference_images=max_refs, nanobanana_variants_per_image_task=1, approval_gate="false")
        ),
        asset_library={
            "category1": {"asset1": "ASSET_1", "asset2": "ASSET_2"}
        },
        image_tasks=[
            NanoBananaImageTask(
                task_id="t1", block_id="b1", shot_id="s1", role="start", 
                refs=refs, 
                prompt="p", approval=NanoBananaApproval(status="OK")
            )
        ]
    )

def test_validate_refs_success():
    # Setup: Request with valid refs within limit
    req = create_mock_request(refs=["ASSET_1", "ASSET_2"])
    
    # Setup: Repo returns valid assets
    mock_repo.get_asset.side_effect = lambda x: Asset(asset_id=x, file_name=f"{x}.png", tipo_asset="img", mv_context_default="c", descripcion_visual="d", uso_sugerido="u") if x in ["ASSET_1", "ASSET_2"] else None
    
    # Mock resolve_file_path to return a value (simulate file exists)
    mock_repo.resolve_file_path.return_value = "/path/to/file.png"

    # Instantiate Use Case with mocks
    use_case = IngestNanoBanana(MagicMock(), mock_repo, mock_logger)
    
    # Test Validation
    # Should not raise exception
    use_case._validate_refs(req)
    print("test_validate_refs_success: PASSED")

def test_validate_refs_max_exceeded():
    req = create_mock_request(refs=["A1", "A2", "A3"], max_refs=2)
    use_case = IngestNanoBanana(MagicMock(), mock_repo, mock_logger)
    
    try:
        use_case._validate_refs(req)
        print("test_validate_refs_max_exceeded: FAILED (No exception raised)")
    except ValueError as e:
        if "exceeding limit" in str(e):
             print("test_validate_refs_max_exceeded: PASSED")
        else:
             print(f"test_validate_refs_max_exceeded: FAILED (Wrong exception: {e})")

def test_validate_refs_missing_in_library():
    req = create_mock_request(refs=["ASSET_UNKNOWN"])
    use_case = IngestNanoBanana(MagicMock(), mock_repo, mock_logger)
    
    try:
        use_case._validate_refs(req)
        print("test_validate_refs_missing_in_library: FAILED (No exception raised)")
    except ValueError as e:
         if "unknown asset ID in JSON" in str(e):
             print("test_validate_refs_missing_in_library: PASSED")
         else:
             print(f"test_validate_refs_missing_in_library: FAILED (Wrong exception: {e})")

if __name__ == "__main__":
    try:
        test_validate_refs_success()
        test_validate_refs_max_exceeded()
        test_validate_refs_missing_in_library()
    except Exception as e:
        print(f"FAILED: {e}")
