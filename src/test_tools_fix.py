import sys
import os
from PIL import Image

# Add src to path
sys.path.append(os.path.abspath("src"))

from editor.editor_core import EditorCore

def test_tools():
    core = EditorCore()
    
    # Create a dummy image
    img = Image.new("RGBA", (100, 100), color="red")
    img_path = "test_image.png"
    img.save(img_path)
    
    try:
        core.load_image(img_path)
        print("Image loaded.")

        # Test Resize
        print("Testing Resize Image...")
        res = core.apply_tool("Resize Image", width=50, height=50)
        assert res.size == (50, 50)
        assert core.original_image.size == (50, 50)
        assert len(core.history) == 1
        print("Resize Image: PASSED")

        # Test Convert (RGBA -> JPEG)
        print("Testing Convert Format (RGBA -> JPEG)...")
        res = core.apply_tool("Convert Format", fmt="JPEG")
        assert res.mode == "RGB"
        assert res.format == "JPEG"
        assert len(core.history) == 2
        print("Convert Format: PASSED")

        # Test Compress
        print("Testing Compress to Size...")
        # Since it's a small solid color image, it should easily compress
        res = core.apply_tool("Compress to Size", target_kb=10)
        assert res is not None
        assert len(core.history) == 3
        print("Compress to Size: PASSED")

        print("\nAll tests PASSED!")

    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

if __name__ == "__main__":
    test_tools()
