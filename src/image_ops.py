from PIL import Image

def apply_grayscale(img: Image.Image) -> Image.Image:
    """Convert image to grayscale."""
    return img.convert("L").convert("RGB")
