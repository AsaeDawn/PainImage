from PIL import Image

FILTER_NAME = "Color Balance"
HAS_PARAMS = True

PARAMS = {
    "red": {
        "min": -100,
        "max": 100,
        "default": 0,
        "label": "Red"
    },
    "green": {
        "min": -100,
        "max": 100,
        "default": 0,
        "label": "Green"
    },
    "blue": {
        "min": -100,
        "max": 100,
        "default": 0,
        "label": "Blue"
    }
}

def run(img: Image.Image, red: int = 0, green: int = 0, blue: int = 0) -> Image.Image:
    img = img.convert("RGB")
    
    if red == 0 and green == 0 and blue == 0:
        return img

    # Use Matrix for speed
    # We are just adding offsets to channels
    # red=100 -> +50 brightness? let's stick to previous logic roughly.
    # Previous logic: val = i + shift
    # shift was just passed directly? No, I decided "shift * 1.0".
    # So red=100 adds 100 to R.
    
    # 4x3 matrix for convert
    # R' = 1*R + 0*G + 0*B + r_shift
    # G' = 0*R + 1*G + 0*B + g_shift
    # B' = 0*R + 0*G + 1*B + b_shift
    
    matrix = [
        1, 0, 0, red,
        0, 1, 0, green,
        0, 0, 1, blue
    ]
    
    return img.convert("RGB", matrix=matrix)
