from PIL import Image, ImageDraw, ImageFilter, ImageChops
import random

FILTER_NAME = "Vignette & Noise"
HAS_PARAMS = True

PARAMS = {
    "vignette_amount": {
        "min": 0,
        "max": 100,
        "default": 0,
        "label": "Vignette Strength"
    },
    "vignette_radius": {
        "min": 0,
        "max": 100,
        "default": 50,
        "label": "Vignette Radius"
    },
    "noise_amount": {
        "min": 0,
        "max": 100,
        "default": 0,
        "label": "Noise Amount"
    }
}

def run(img: Image.Image, vignette_amount: int = 0, vignette_radius: int = 50, noise_amount: int = 0) -> Image.Image:
    img = img.convert("RGB")
    width, height = img.size

    # --- Vignette ---
    if vignette_amount > 0:
        # Create a gradient mask
        # Radius: 0 -> full black, 100 -> only corners
        # Let's map radius 0-100 to a scale of the image size
        
        # Base radius: half diagonal
        import math
        diag = math.sqrt(width*width + height*height) / 2.0
        
        # Radius adjustment
        # If slider is 50 (default), we want "standard" look.
        # If slider is 100, the clear circle is very large (subtle vignette).
        # If slider is 0, the clear circle is tiny.
        
        img_scale = max(width, height)
        # map 0-100 to 0.1 - 2.0 size relative to center
        r_scale = 0.5 + (vignette_radius / 100.0) * 1.5
        
        # Create radial gradient is tricky in pure PIL without numpy
        # Approximating with a drawn ellipse blur
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        c_x, c_y = width // 2, height // 2
        radius_x = width * r_scale * 0.8
        radius_y = height * r_scale * 0.8
        
        draw.ellipse((c_x - radius_x, c_y - radius_y, c_x + radius_x, c_y + radius_y), fill=255)
        
        # Blur the mask to create gradient
        blur_radius = img_scale * 0.2  # significant blur
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Apply mask
        # Vignette darkens borders. 
        # Layer: black image. Mask: calculated mask.
        # Composite: if mask is white, show original. If black, show black?
        # Actually standard vignette is darken. 
        # Multiply approach: 
        # Invert mask so center is white (keep) and corners black (darken)? 
        # Wait, I drew white in center. So white = keep original.
        
        # Intensity control
        # If intensity is low, the black borders shouldn't be fully black.
        # We can lift the black point of the mask.
        
        if vignette_amount < 100:
            # lift blacks
            lift = int((100 - vignette_amount) * 2.55)
            # map black(0) to lift, white(255) stays white
            # point fn: x -> lift + x * (255-lift)/255
            def lift_fn(x):
                return lift + x * (255 - lift) / 255
            mask = mask.point(lift_fn)
            
        black_layer = Image.new('RGB', (width, height), (0, 0, 0))
        img = Image.composite(img, black_layer, mask)

    # --- Noise ---
    if noise_amount > 0:
        # Generate noise
        # Creating a noise image pixel-by-pixel is slow.
        # Optimization: Create small noise tile and tile it?
        # Or use a fixed random buffer approach if possible.
        # For now, let's try a small tile stretch method for performance, 
        # or just rand over full image if size is small (proxy).
        # Since this runs on proxy often, it might be ok.
        
        # Let's map amount 0-100 to alpha 0-128
        alpha = int((noise_amount / 100.0) * 100)
        
        # Create noise layer
        # EffectType: Gaussian noise or simpler uniform noise
        # PIL doesn't have native noise generator.
        # We can use ImageEffect.noise if available? No.
        
        # Faster Hack:
        # Create a small noise image map and resize (nearest neighbor) -> blocky noise
        # Create a detailed noise map -> slow
        
        # Let's use the `random` module efficiently?
        # map bytes
        import os
        noise_data = os.urandom(width * height)
        # This gives uniform 0-255.
        noise_img = Image.frombytes('L', (width, height), noise_data)
        
        # Blend mode: Overlay or Soft Light is best for grain.
        # Normal blend with low opacity is easier.
        
        noise_layer = noise_img.convert("RGB")
        
        # Composite with alpha
        if alpha > 0:
            # blend
            img = Image.blend(img, noise_layer, alpha / 500.0) # very subtle blend needed

    return img
