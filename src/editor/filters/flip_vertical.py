from PIL import Image

FILTER_NAME = "Flip Vertical"

def run(img: Image.Image) -> Image.Image:
    return img.transpose(Image.FLIP_TOP_BOTTOM)
