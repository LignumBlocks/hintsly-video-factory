import unittest
from domain.nanobanana_models import NanoBananaStylePresets, NanoBananaImageTask, NanoBananaApproval
from usecases.nanobanana_prompt_service import NanoBananaPromptService

class TestStrictAdherence(unittest.TestCase):
    def setUp(self):
        self.service = NanoBananaPromptService()

    def test_strict_concatenation(self):
        """
        HU-09: Prove strict determinism. 
        Output MUST BE exactly 'Global Style + Task Prompt'.
        No extra words, no rephrasing, no hidden injections.
        """
        style = NanoBananaStylePresets(
            global_image_style="StyleA.",
            global_negative_append="NegA"
        )
        task = NanoBananaImageTask(
            task_id="t1", block_id="b", shot_id="s", role="r", variants=1, refs=[], 
            prompt="PromptB.", output={"res": "1"}, 
            approval=NanoBananaApproval(status="PENDING", notes="")
        )
        
        # ACT
        final_prompt = self.service.construct_prompt(style, task)
        
        # ASSERT
        expected = "StyleA. PromptB."
        self.assertEqual(final_prompt, expected, 
            f"Violation of strictly declarative logic.\nExpected: '{expected}'\nGot: '{final_prompt}'")
        
        # Check negative prompt structure just in case
        final_neg = self.service.construct_negative_prompt(style, task)
        expected_neg = "NegA"
        self.assertEqual(final_neg, expected_neg)

    def test_no_injections_on_empty(self):
        """Ensure no defaults are injected if inputs are empty."""
        style = NanoBananaStylePresets(global_image_style="", global_negative_append="")
        task = NanoBananaImageTask(
            task_id="t1", block_id="b", shot_id="s", role="r", variants=1, refs=[], 
            prompt="Simple.", output={"res": "1"}, approval=NanoBananaApproval(status="PENDING", notes=""))
            
        final_prompt = self.service.construct_prompt(style, task)
        self.assertEqual(final_prompt, "Simple.")

if __name__ == '__main__':
    unittest.main()
