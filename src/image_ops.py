from PIL import Image

def apply_grayscale(img: Image.Image) -> Image.Image:
    """Convert image to grayscale."""
    return img.convert("L").convert("RGB")

def rotate_left(img: Image.Image) -> Image.Image:
    return img.rotate(90, expand=True)

def rotate_right(img: Image.Image) -> Image.Image:
    return img.rotate(-90, expand=True)