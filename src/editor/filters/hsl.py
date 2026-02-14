from PIL import Image
import colorsys

FILTER_NAME = "HSL Adjustment"
HAS_PARAMS = True

PARAMS = {
    "hue": {
        "min": -180,
        "max": 180,
        "default": 0,
        "label": "Hue"
    },
    "saturation": {
        "min": -100,
        "max": 100,
        "default": 0,
        "label": "Saturation"
    },
    "lightness": {
        "min": -100,
        "max": 100,
        "default": 0,
        "label": "Lightness"
    }
}

def run(img: Image.Image, hue: int = 0, saturation: int = 0, lightness: int = 0) -> Image.Image:
    # Convert to RGB to ensure we can manipulate pixels
    img = img.convert("RGB")
    
    # If no changes, return original
    if hue == 0 and saturation == 0 and lightness == 0:
        return img

    # Normalize parameters
    # Hue: -180..180 -> -0.5..0.5 (colorsys uses 0..1, wrapping around)
    h_norm = hue / 360.0
    # Saturation: -100..100 -> percentage change. 0 is no change. 
    # We'll treat current saturation as S. New S' = S * (1 + s_norm)
    s_norm = saturation / 100.0
    # Lightness: -100..100 -> percentage change
    l_norm = lightness / 100.0

    # Get pixel data
    pixels = img.load()
    width, height = img.size

    # Process pixels
    # Note: This is slow in pure Python. Ideally we'd use numpy or a C extension.
    # But sticking to pure PIL/Python as per request/environment constraints.
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # Convert to HLS
            # colorsys uses 0..1 for all
            h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
            
            # Modify Hue
            h = (h + h_norm) % 1.0
            
            # Modify Saturation
            # Simple scaling: if s_norm > 0, we approach 1. If s_norm < 0, we approach 0.
            if s_norm > 0:
                s = s + (1.0 - s) * s_norm
            else:
                s = s * (1.0 + s_norm)
            s = max(0.0, min(1.0, s))

            # Modify Lightness
            if l_norm > 0:
                l = l + (1.0 - l) * l_norm
            else:
                l = l * (1.0 + l_norm)
            l = max(0.0, min(1.0, l))
            
            # Convert back to RGB
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            
            pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255))

    return img
