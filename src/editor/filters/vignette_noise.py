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

    # --- Vignette (Optimized) ---
    if vignette_amount > 0:
        # Instead of creating a mask at full resolution (e.g., 4K), 
        # create it at a small fixed size and upscale.
        # This makes the GaussianBlur constant time regardless of image size.
        
        small_w, small_h = 256, 256 # Fixed low resolution for mask
        
        # Calculate aspect ratio to keep vignette shape correct
        aspect = width / height
        if aspect > 1:
            draw_w, draw_h = small_w, int(small_w / aspect)
        else:
            draw_w, draw_h = int(small_h * aspect), small_h
            
        mask = Image.new('L', (draw_w, draw_h), 0)
        draw = ImageDraw.Draw(mask)
        
        c_x, c_y = draw_w // 2, draw_h // 2
        
        # Radius logic
        r_scale = 0.5 + (vignette_radius / 100.0) * 1.5
        radius_x = draw_w * r_scale * 0.8
        radius_y = draw_h * r_scale * 0.8
        
        draw.ellipse((c_x - radius_x, c_y - radius_y, c_x + radius_x, c_y + radius_y), fill=255)
        
        # Blur on small image is fast
        blur_radius = max(draw_w, draw_h) * 0.2
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Lift blacks if needed
        if vignette_amount < 100:
            lift = int((100 - vignette_amount) * 2.55)
            # Apply point transform on small image (fast)
            mask = mask.point(lambda x: lift + x * (255 - lift) / 255)

        # Upscale mask to full size
        # BILINEAR is fast and smooth enough for a blurry mask
        mask = mask.resize((width, height), Image.Resampling.BILINEAR)
        
        # Composite
        black_layer = Image.new('RGB', (width, height), (0, 0, 0))
        img = Image.composite(img, black_layer, mask)

    # --- Noise (Optimized) ---
    if noise_amount > 0:
        # Generate noise
        # Optimization: Generate a smaller noise patch and tile it, 
        # or use a very fast method.
        # Actually random.effect_noise is not available.
        # But generating 1MB of random bytes is fast (1024x1024).
        # For 4K, it might be 24MB. 
        # Let's stick to full res generation but check if we can skip if noise_amount is low.
        
        alpha = int((noise_amount / 100.0) * 100)
        if alpha > 0:
            # We can use a lower resolution noise and scale it up with Nearest neighbor 
            # to give a "pixelated" grain look which is often stylish, 
            # reducing generation cost.
            # Or just generate full res. os.urandom is roughly 200MB/s. 
            # 4K image (8MP) -> 8MB. Instant.
            # The slow part might be Image.frombytes overhead or blending.
            
            import os
            noise_data = os.urandom(width * height)
            noise_img = Image.frombytes('L', (width, height), noise_data)
            noise_layer = noise_img.convert("RGB")
            
            # Blend is fast in C
            img = Image.blend(img, noise_layer, alpha / 500.0)

    return img
