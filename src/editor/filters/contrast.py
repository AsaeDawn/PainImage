from PIL import Image, ImageEnhance

FILTER_NAME = "Contrast"
HAS_PARAMS = True

PARAMS = {
    "delta": {
        "min": -100,
        "max": 100,
        "default": 0
    }
}

def run(img: Image.Image, delta: int = 0) -> Image.Image:
    factor = 1.0 + (delta / 100.0)
    factor = max(0.0, factor)
    return ImageEnhance.Contrast(img).enhance(factor)
