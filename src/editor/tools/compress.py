import io
from PIL import Image

TOOL_NAME = "Compress to Size"

def run(img: Image.Image, target_kb: int) -> Image.Image:
    """
    Compress image to approximate target file size (KB) using Binary Search.
    Returns compressed Image.
    """
    target_bytes = target_kb * 1024
    img_format = "JPEG"
    
    low = 5
    high = 95
    best_quality = 10
    best_buffer = None
    
    # Binary search for the highest quality that fits inside target_bytes
    for _ in range(7):  # ~7 iterations is enough for 5-95 range
        if low > high:
            break
            
        mid = (low + high) // 2
        buffer = io.BytesIO()
        img.save(buffer, format=img_format, quality=mid)
        size = buffer.getbuffer().nbytes
        
        if size <= target_bytes:
            best_quality = mid
            best_buffer = buffer
            low = mid + 1
        else:
            high = mid - 1
            
    if best_buffer:
        best_buffer.seek(0)
        return Image.open(best_buffer).copy()
    
    # Fallback to quality 10 if nothing fit
    buffer = io.BytesIO()
    img.save(buffer, format=img_format, quality=10)
    buffer.seek(0)
    return Image.open(buffer).copy()
