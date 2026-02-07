import sys
import os
from PIL import Image

# Add src to path
sys.path.append(os.path.abspath("src"))

from editor.editor_core import EditorCore

def test_slider_logic():
    core = EditorCore()
    
    # Create a dummy image
    img = Image.new("RGB", (100, 100), color="white")
    img_path = "test_slider.png"
    img.save(img_path)
    
    try:
        core.load_image(img_path)
        print("Image loaded.")

        # Simulate slider change (Brightness +20)
        print("Simulating Brightness +20...")
        core.in_preview = True
        filter_list = [("Brightness", {"delta": 40})] # slider 70 -> delta 40
        core.apply_preview_filters(filter_list)
        
        preview1 = core.current_image.copy()
        print(f"Preview 1 mean: {sum(preview1.getdata())/30000:.2f}")

        # Push history with slider state
        slider_state = {"Brightness": 70}
        core.push_history(slider_state)
        print("Pushed history with state.")

        # Simulate another slider change (Contrast +10)
        # In current broken logic, if we committed preview, the next preview would be on top of preview1.
        # In fixed logic, it should still be on top of original_image.
        print("Simulating Contrast +20...")
        filter_list.append(("Contrast", {"delta": 20}))
        core.apply_preview_filters(filter_list)
        
        preview2 = core.current_image.copy()
        print(f"Preview 2 mean: {sum(preview2.getdata())/30000:.2f}")

        # Undo
        print("Testing Undo...")
        restored_state = core.undo(current_slider_state={"Brightness": 70, "Contrast": 60})
        assert restored_state == slider_state
        print("Undo restored correct slider state: PASSED")

        # Test Baking before destructive filter
        print("Testing Commit before destructive filter...")
        core.commit_preview(filter_list)
        assert core.original_image.size == (100, 100) # Size shouldn't change, but pixels should
        
        # Verify it's not double applied
        # If we commit, original_image becomes preview2.
        # If we then move a slider again (e.g. Brightness back to 50), it should be relative to NEW original_image.
        
        print("\nSlider logic tests completed!")

    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

if __name__ == "__main__":
    test_slider_logic()
