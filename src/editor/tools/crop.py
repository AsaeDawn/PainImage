from PIL import Image

TOOL_NAME = "Crop Image"

def run(img: Image.Image, box: tuple) -> Image.Image:
    """
    Crop the image.
    :param img: PIL Image
    :param box: (left, top, right, bottom)
    :return: Cropped PIL Image
    """
    if not box:
        return img
    return img.crop(box)
