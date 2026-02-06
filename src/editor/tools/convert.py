from PIL import Image

TOOL_NAME = "Convert Format"

def run(img: Image.Image, fmt: str):
    fmt = fmt.upper()

    if fmt not in ["JPEG", "PNG", "WEBP"]:
        fmt = "PNG"

    # If converting to JPEG, ensure we are in RGB mode (discard alpha)
    if fmt == "JPEG" and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    img.format = fmt
    return img
