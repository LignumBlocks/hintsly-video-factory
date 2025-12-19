import logging
import unittest
from adapters.nanobanana_repository import NanoBananaRepository
from domain.nanobanana_models import (
    NanoBananaRequest, NanoBananaProject, NanoBananaOutputConfig, 
    NanoBananaProductionRules, NanoBananaImageTask, NanoBananaApproval, NanoBananaFileInfo
)
from usecases.run_nanobanana_generation import RunNanoBananaGeneration
from unittest.mock import MagicMock

# Simple Mock Logger
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARN: {msg}")
    def debug(self, msg): print(f"DEBUG: {msg}")

class TestApprovalGate(unittest.TestCase):
    def setUp(self):
        self.repo = NanoBananaRepository()
        self.logger = MockLogger()
        # Minimal mocks for dependencies we don't need for this specific test logic
        self.use_case = RunNanoBananaGeneration(
            repository=self.repo,
            prompt_service=MagicMock(),
            client=MagicMock(),
            assets_repository=MagicMock(),
            logger=self.logger
        )

    def create_project(self, approval_gate_rule="REQUIRED"):
        return NanoBananaRequest(
            file_info=NanoBananaFileInfo(pipeline_context="test", version="1", target_tool="n"),
            project=NanoBananaProject(
                project_id="gate_test",
                title="Test",
                scope_blocks_included=[],
                output=NanoBananaOutputConfig(aspect_ratio="16:9", resolution_px="1K", image_format="png"),
                production_rules=NanoBananaProductionRules(
                    nanobanana_max_reference_images=5,
                    nanobanana_variants_per_image_task=1,
                    approval_gate=approval_gate_rule
                )
            ),
            asset_library={},
            image_tasks=[
                NanoBananaImageTask(
                    task_id="t1", block_id="b", shot_id="s", role="r", variants=1, refs=[], prompt="p",
                    output={"res": "1"}, approval=NanoBananaApproval(status="PENDING_REVIEW", notes="")
                ),
                NanoBananaImageTask(
                    task_id="t2", block_id="b", shot_id="s", role="r", variants=1, refs=[], prompt="p",
                    output={"res": "1"}, approval=NanoBananaApproval(status="PENDING_REVIEW", notes="")
                )
            ]
        )

    def test_gate_active_pending_tasks(self):
        """Should fail if gate is active and tasks are not APPROVED"""
        req = self.create_project(approval_gate_rule="REQUIRED")
        self.repo.save(req)
        
        allowed = self.use_case.check_project_approval("gate_test")
        self.assertFalse(allowed, "Should block when tasks are PENDING_REVIEW and gate is active")

    def test_gate_active_all_approved(self):
        """Should pass if gate is active but all tasks are APPROVED"""
        req = self.create_project(approval_gate_rule="REQUIRED")
        # Approve all
        for t in req.image_tasks:
            t.approval.status = "APPROVED"
        self.repo.save(req)
        
        allowed = self.use_case.check_project_approval("gate_test")
        self.assertTrue(allowed, "Should pass when all tasks are APPROVED")

    def test_gate_inactive(self):
        """Should pass regardless of status if gate is inactive"""
        # "none", "", or "false" could be considered inactive depending on logic.
        # Logic implemented: gate_active = rule != "none"
        req = self.create_project(approval_gate_rule="none")
        self.repo.save(req)
        
        allowed = self.use_case.check_project_approval("gate_test")
        self.assertTrue(allowed, "Should pass when approval_gate is 'none'")

    def test_rejection_blocks(self):
         """Should block if a task is REJECTED"""
         req = self.create_project(approval_gate_rule="REQUIRED")
         req.image_tasks[0].approval.status = "APPROVED"
         req.image_tasks[1].approval.status = "REJECTED"
         self.repo.save(req)
         
         allowed = self.use_case.check_project_approval("gate_test")
         self.assertFalse(allowed, "Should block if any task is REJECTED")

if __name__ == '__main__':
    unittest.main()
