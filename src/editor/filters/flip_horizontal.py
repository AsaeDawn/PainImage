from PIL import Image

FILTER_NAME = "Flip Horizontal"

def run(img: Image.Image) -> Image.Image:
    return img.transpose(Image.FLIP_LEFT_RIGHT)
