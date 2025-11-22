from PIL import Image, ImageFilter

FILTER_NAME = "Blur"

def run(img: Image.Image) -> Image.Image:
    return img.filter(ImageFilter.GaussianBlur(radius=5))

