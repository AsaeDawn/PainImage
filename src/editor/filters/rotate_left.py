from PIL import Image

FILTER_NAME = "Rotate Left"

def run(img: Image.Image) -> Image.Image:
    return img.rotate(90, expand=True)
