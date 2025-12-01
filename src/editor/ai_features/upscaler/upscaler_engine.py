import torch
from realesrgan import RealESRGAN
from PIL import Image

class UpscalerEngine:
    def __init__(self, model_path):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_path = model_path
        self.model = None

    def load(self):
        if self.model is None:
            self.model = RealESRGAN(self.device, scale=4)
            self.model.load_weights(self.model_path, download=False)

    def upscale(self, pil_image):
        """Takes PIL Image -> returns PIL Image (upscaled)."""
        self.load()
        return self.model.predict(pil_image)
