import os
from .upscaler_engine import UpscalerEngine
from .upscale_manager import UpscaleModelManager

AI_NAME = "Upscaler"

class UpscalerFeature:
    def __init__(self):
        self.manager = UpscaleModelManager()
        self.engine = UpscalerEngine(self.manager.model_dir)

    def upscale(self, img):
        return self.engine.upscale(img)

AI_CLASS = UpscalerFeature
