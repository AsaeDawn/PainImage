from PIL import Image

TOOL_NAME = "Resize Image"

def run(img: Image.Image, width: int, height: int) -> Image.Image:
    return img.resize((width, height), Image.Resampling.LANCZOS)
