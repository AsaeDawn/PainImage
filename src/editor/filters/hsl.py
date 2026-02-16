from PIL import Image
import math

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
    # Optimized implementation using Color Matrix
    # This avoids the slow pixel-by-pixel Python loop
    
    img = img.convert("RGB")
    
    if hue == 0 and saturation == 0 and lightness == 0:
        return img

    # 1. HUE ROTATION Matrix
    # Rotate around the grey vector (1,1,1)
    # Cos/Sin of hue angle
    angle = math.radians(hue)
    c = math.cos(angle)
    s = math.sin(angle)
    
    # Weights for luminance (approx)
    lum_r = 0.213
    lum_g = 0.715
    lum_b = 0.072
    
    # Hue matrix coefficients
    # https://docs.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-rotating-colors-use
    # Simplified approach:
    # R column
    m00 = c + (1.0 - c) * lum_r
    m01 = (1.0 - c) * lum_g - s * lum_b # wait, the math is complex.
    
    # Let's use a standard implementation for Hue Rotation matrix
    # Derived from: http://www.graficaobscura.com/matrix/index.html
    
    w = 1.0/3.0 # uniform weights for rotation axis often used, or lum weights
    # Using 1/3 for pure geometric rotation in RGB cube usually preserves range better for simple usage
    sq3 = math.sqrt(3) # Not needed if using predetermined coefficients
    
    # Actually, let's construct the matrix steps:
    # M = Lightness * Saturation * Hue
    
    # --- Hue Matrix (approximate rotation keeping gray axis fixed) ---
    # Using approximations for "unweighted" RGB rotation
    m_hue = [
        # R output
        c + (1-c)/3.0,       (1-c)/3.0 - s/math.sqrt(3), (1-c)/3.0 + s/math.sqrt(3), 0,
        # G output
        (1-c)/3.0 + s/math.sqrt(3), c + (1-c)/3.0,       (1-c)/3.0 - s/math.sqrt(3), 0,
        # B output
        (1-c)/3.0 - s/math.sqrt(3), (1-c)/3.0 + s/math.sqrt(3), c + (1-c)/3.0,       0
    ]
    
    # --- Saturation Matrix ---
    # Interpolate between Identity and Grayscale
    # S > 0: linear saturation boost? 
    # S = -100 (0.0) -> Grayscale. S=0 (1.0) -> Normal. S=100 (2.0) -> Double.
    sat_scale = 1.0 + (saturation / 100.0)
    if sat_scale < 0: sat_scale = 0
    
    sr = (1 - sat_scale) * lum_r
    sg = (1 - sat_scale) * lum_g
    sb = (1 - sat_scale) * lum_b
    
    m_sat = [
        sr + sat_scale, sr, sr, 0,
        sg, sg + sat_scale, sg, 0,
        sb, sb, sb + sat_scale, 0
    ]
    
    # --- Lightness (Brightness) Matrix ---
    # Simply shift or scale
    # Current implementation in slider was:
    # l_norm > 0: l + (1-l)*l_norm
    # This is hard to do with matrix perfectly (it's conditional).
    # Simple brightness Matrix: Scale * pixel + offset
    # Let's use simple offset for -100..100 -> -255..255 shift?
    # Or scale?
    # Brightness typically adds offset.
    light_offset = lightness * 2.55 # -255 to 255
    
    # Combine Matrices?
    # PIL convert() takes one matrix. We need to multiply them.
    # We can chain transforms or multipy matrices in python.
    # M_total = M_hue * M_sat (approximately)
    # Lightness is just an offset added to the 4th column of the matrix.
    
    def mult(m1, m2):
        # 4x3 * 4x3 ? 
        # m1 is applied on (R,G,B,1). 
        # Treat as 4x4 with last row 0,0,0,1
        res = [0]*12
        for r in range(3):
            for c_idx in range(4):
                val = 0
                for k in range(4):
                    # m1[r, k] * m2[k, c_idx]
                    # m1 is row-major 3 rows x 4 cols
                    
                    # Element from m1 at row r, col k
                    v1 = m1[r*4 + k]
                    
                    # Element from m2 at row k, col c_idx
                    if k < 3:
                        v2 = m2[k*4 + c_idx]
                    else:
                        # Bottom row of m2 is 0,0,0,1
                        v2 = 1.0 if c_idx == 3 else 0.0
                        
                    val += v1 * v2
                res[r*4 + c_idx] = val
        return res

    # Combine Hue and Sat
    m_final = mult(m_sat, m_hue)
    
    # Add Lightness to the offset column (indices 3, 7, 11)
    # This is a post-transform offset: Output = M*Input + Offset
    m_final[3] += light_offset
    m_final[7] += light_offset
    m_final[11] += light_offset
    
    return img.convert("RGB", matrix=m_final)
