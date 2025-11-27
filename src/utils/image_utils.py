from PIL import Image
from PySide6.QtGui import QImage, QPixmap
import io

def pil_image_to_qpixmap(pil_img: Image.Image) -> QPixmap:
    """Convert PIL.Image to QPixmap."""
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")
    data = pil_img.tobytes("raw", "RGBA")
    qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimg)
