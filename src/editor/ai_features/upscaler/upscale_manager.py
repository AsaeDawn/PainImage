import os
import sys

class UpscaleModelManager:
    def __init__(self):
        self.model_dir = os.path.join(
            os.path.dirname(__file__), "model"
        )

    def exists(self):
        # Check platform-specific binary
        if sys.platform == "win32":
            binary_path = os.path.join(self.model_dir, "windows", "realesrgan-ncnn-vulkan.exe")
        else:
            binary_path = os.path.join(self.model_dir, "linux", "realesrgan-ncnn-vulkan")

        models_dir = os.path.join(self.model_dir, "models")

        return (
            os.path.exists(binary_path) and
            os.path.exists(os.path.join(models_dir, "realesrgan-x4plus.bin")) and
            os.path.exists(os.path.join(models_dir, "realesrgan-x4plus.param"))
        )

    def download(self, progress_callback=None):
        import urllib.request
        
        # Using HuggingFace mirror for more reliable large file downloads
        # GitHub Raw (LFS) can sometimes fail with 404 on direct urlretrieve
        base_urls = [
            "https://huggingface.co/caidas/real-esrgan-ncnn-vulkan/resolve/main/models/",
            "https://raw.githubusercontent.com/xinntao/Real-ESRGAN-ncnn-vulkan/master/models/",
            "https://raw.githubusercontent.com/xinntao/Real-ESRGAN-ncnn-vulkan/main/models/"
        ]
        files = ["realesrgan-x4plus.bin", "realesrgan-x4plus.param"]
        
        total_steps = len(files)
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)

        # Add User-Agent
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
        urllib.request.install_opener(opener)

        for i, filename in enumerate(files):
            success = False
            last_err = None
            
            for base_url in base_urls:
                url = base_url + filename
                target_path = os.path.join(self.model_dir, filename)
                
                try:
                    def _report(block_num, block_size, total_size):
                        if progress_callback and total_size > 0:
                            file_progress = (block_num * block_size) / total_size
                            overall_progress = int(((i + file_progress) / total_steps) * 100)
                            progress_callback(min(99, overall_progress))

                    urllib.request.urlretrieve(url, target_path, reporthook=_report if progress_callback else None)
                    success = True
                    break
                except Exception as e:
                    last_err = e
                    continue
            
            if not success:
                print(f"Failed to download {filename} from all mirrors: {last_err}")
                raise last_err
        
        if progress_callback:
            progress_callback(100)
