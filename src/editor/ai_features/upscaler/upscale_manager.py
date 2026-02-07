import os

class UpscaleModelManager:
    def __init__(self):
        self.model_dir = os.path.join(
            os.path.dirname(__file__), "model"
        )

    def exists(self):
        import sys
        binary_name = "realesrgan-ncnn-vulkan"
        if sys.platform == "win32":
            binary_name += ".exe"

        return (
            os.path.exists(os.path.join(self.model_dir, binary_name)) and
            os.path.exists(os.path.join(self.model_dir, "realesrgan-x4plus.bin")) and
            os.path.exists(os.path.join(self.model_dir, "realesrgan-x4plus.param"))
        )

    def download(self, progress_callback=None):
        # Not needed right now since your files are already present
        pass
