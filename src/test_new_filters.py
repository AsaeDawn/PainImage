import os
import sys
from PIL import Image

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from editor.filters import hsl, color_balance, levels, vignette_noise

def test_filters():
    print("Creating test image...")
    img = Image.new("RGB", (200, 200), (100, 100, 100))
    
    print("Testing HSL...")
    res = hsl.run(img, hue=10, saturation=10, lightness=10)
    assert res is not None
    assert res.size == (200, 200)
    print("HSL OK")
    
    print("Testing Color Balance...")
    res = color_balance.run(img, red=10, green=-10, blue=50)
    assert res is not None
    print("Color Balance OK")

    print("Testing Levels...")
    res = levels.run(img, shadows=10, midtones=120, highlights=240)
    assert res is not None
    print("Levels OK")

    print("Testing Vignette...")
    res = vignette_noise.run(img, vignette_amount=50, vignette_radius=50)
    assert res is not None
    print("Vignette OK")

    print("Testing Noise...")
    res = vignette_noise.run(img, noise_amount=30)
    assert res is not None
    print("Noise OK")

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_filters()
