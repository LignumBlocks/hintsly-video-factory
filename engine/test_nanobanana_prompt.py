from usecases.nanobanana_prompt_service import NanoBananaPromptService
from domain.nanobanana_models import NanoBananaStylePresets, NanoBananaImageTask, NanoBananaApproval

def create_dummy_task(prompt="My Prompt", neg="My Negative"):
    return NanoBananaImageTask(
        task_id="t1", block_id="b1", shot_id="s1", role="start", refs=[], 
        prompt=prompt, negative_prompt=neg, approval=NanoBananaApproval(status="OK")
    )

def test_prompt_concatenation():
    service = NanoBananaPromptService()
    style = NanoBananaStylePresets(global_image_style="GlobalStyle", global_negative_append="GlobalNeg")
    task = create_dummy_task(prompt="TaskPrompt", neg="TaskNeg")
    
    final_prompt = service.construct_prompt(style, task)
    final_neg = service.construct_negative_prompt(style, task)
    
    # Assertions
    assert final_prompt == "GlobalStyle TaskPrompt"
    assert final_neg == "GlobalNeg, TaskNeg"
    print("test_prompt_concatenation: PASSED")

def test_prompt_empty_styles():
    service = NanoBananaPromptService()
    style = None
    task = create_dummy_task(prompt="OnlyTask", neg="OnlyTaskNeg")
    
    final_prompt = service.construct_prompt(style, task)
    final_neg = service.construct_negative_prompt(style, task)
    
    assert final_prompt == "OnlyTask"
    assert final_neg == "OnlyTaskNeg"
    print("test_prompt_empty_styles: PASSED")

def test_prompt_empty_fields_handling():
    service = NanoBananaPromptService()
    style = NanoBananaStylePresets(global_image_style="", global_negative_append="")
    task = create_dummy_task(prompt="JustPrompt", neg="")
    
    final_prompt = service.construct_prompt(style, task)
    final_neg = service.construct_negative_prompt(style, task)
    
    assert final_prompt == "JustPrompt"
    assert final_neg == ""
    print("test_prompt_empty_fields_handling: PASSED")

if __name__ == "__main__":
    try:
        test_prompt_concatenation()
        test_prompt_empty_styles()
        test_prompt_empty_fields_handling()
    except Exception as e:
        print(f"FAILED: {e}")
