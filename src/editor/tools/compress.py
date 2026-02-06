import io
from PIL import Image

TOOL_NAME = "Compress to Size"

def run(img: Image.Image, target_kb: int) -> Image.Image:
    """
    Compress image to approximate target file size (KB).
    Returns compressed Image.
    """
    target_bytes = target_kb * 1024
    quality = 95
    step = 5

    img_format = "JPEG"

    while quality > 5:
        buffer = io.BytesIO()
        img.save(buffer, format=img_format, quality=quality)
        size = buffer.getbuffer().nbytes

        if size <= target_bytes:
            buffer.seek(0)
            return Image.open(buffer).copy()

        quality -= step

    buffer = io.BytesIO()
    img.save(buffer, format=img_format, quality=10)
    buffer.seek(0)
    return Image.open(buffer).copy()
