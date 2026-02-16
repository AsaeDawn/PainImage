from PIL import Image, ImageOps

FILTER_NAME = "Levels"
HAS_PARAMS = True

PARAMS = {
    "shadows": {
        "min": 0,
        "max": 255,
        "default": 0,
        "label": "Shadows"
    },
    "midtones": {
        "min": 0,
        "max": 200, # 0.0 to 2.0 * 100
        "default": 100, # 1.0 gamma
        "label": "Midtones"
    },
    "highlights": {
        "min": 0,
        "max": 255,
        "default": 255, # Input white point
        "label": "Highlights"
    }
}

def run(img: Image.Image, shadows: int = 0, midtones: int = 100, highlights: int = 255) -> Image.Image:
    img = img.convert("RGB")
    
    # Input verification
    if shadows >= highlights:
        # Avoid division by zero or inversion
        highlights = shadows + 1
        
    gamma = midtones / 100.0
    if gamma <= 0.01: gamma = 0.01
    inv_gamma = 1.0 / gamma

    # Create lookup table
    lut = []
    for i in range(256):
        # 1. Map input [shadows, highlights] to [0, 1]
        val = (i - shadows) / float(highlights - shadows)
        val = max(0.0, min(1.0, val))
        
        # 2. Apply Gamma
        val = val ** inv_gamma
        
        # 3. Scale back to [0, 255]
        val = int(val * 255)
        lut.append(val)
        
    # Apply to all channels (Luminance levels)
    # If we want per-channel execution, code structure would differ.
    # This applies the same curve to R, G, and B
    return img.point(lut * 3 if img.mode == 'RGB' else lut)
