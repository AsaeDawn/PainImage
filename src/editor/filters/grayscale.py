from PIL import Image

FILTER_NAME = "Grayscale"

def run(img: Image.Image) -> Image.Image:
    return img.convert("L").convert("RGB")
