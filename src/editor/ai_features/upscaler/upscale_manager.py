import os
import urllib.request

class UpscalerModelManager:
    def __init__(self):
        self.model_dir = "editor/ai_features/upscaler/model"
        self.model_path = os.path.join(self.model_dir, "realesrgan_x4_lite.pth")
        self.model_url = "https://yourserver.com/models/realesrgan_x4_lite.pth"

    def model_exists(self):
        return os.path.exists(self.model_path)

    def download_model(self, progress_callback=None):
        os.makedirs(self.model_dir, exist_ok=True)

        def report(count, block_size, total_size):
            if progress_callback:
                percent = int(count * block_size * 100 / total_size)
                progress_callback(percent)

        urllib.request.urlretrieve(self.model_url, self.model_path, report)
        return self.model_path
