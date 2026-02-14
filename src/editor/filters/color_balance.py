from PIL import Image

FILTER_NAME = "Color Balance"
HAS_PARAMS = True

PARAMS = {
    "red": {
        "min": -100,
        "max": 100,
        "default": 0,
        "label": "Red"
    },
    "green": {
        "min": -100,
        "max": 100,
        "default": 0,
        "label": "Green"
    },
    "blue": {
        "min": -100,
        "max": 100,
        "default": 0,
        "label": "Blue"
    }
}

def run(img: Image.Image, red: int = 0, green: int = 0, blue: int = 0) -> Image.Image:
    img = img.convert("RGB")
    
    if red == 0 and green == 0 and blue == 0:
        return img

    # Simple lookup table approach for speed
    def get_lut(shift):
        lut = []
        for i in range(256):
            # Shift value. 
            # 100 shift means mapping 0->0, 128->255?
            # Let's try simple addition with clamping
            # Shift of 100 adds 100 to the value? That's too strong.
            # Let's say max shift adds/subtracts 50 intensity levels?
            val = i + (shift * 1.0) # scaling shift if needed
            val = max(0, min(255, int(val)))
            lut.append(val)
        return lut

    # 1.0 means full shift?
    # Let's map -100..100 to -100..100 pixel values for now, effectively changing brightness of channel
    # Or maybe midtone shift?
    
    # Let's use image split and point transforms
    r_lut = get_lut(red)
    g_lut = get_lut(green)
    b_lut = get_lut(blue)
    
    bands = img.split()
    r = bands[0].point(r_lut)
    g = bands[1].point(g_lut)
    b = bands[2].point(b_lut)
    
    return Image.merge("RGB", (r, g, b))
