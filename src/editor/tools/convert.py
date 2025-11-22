from PIL import Image

TOOL_NAME = "Convert Format"

def run(img: Image.Image, fmt: str):
    fmt = fmt.upper()

    if fmt not in ["JPEG", "PNG", "WEBP"]:
        fmt = "PNG"

    img.format = fmt
    return img
