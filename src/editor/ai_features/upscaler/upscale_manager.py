import os

class UpscaleModelManager:
    def __init__(self):
        self.model_dir = os.path.join(
            os.path.dirname(__file__), "model"
        )

    def exists(self):
        return (
            os.path.exists(os.path.join(self.model_dir, "realesrgan-ncnn-vulkan")) and
            os.path.exists(os.path.join(self.model_dir, "realesrgan-x4.bin")) and
            os.path.exists(os.path.join(self.model_dir, "realesrgan-x4.param"))
        )

    def download(self, progress_callback=None):
        # Not needed right now since your files are already present
        pass
