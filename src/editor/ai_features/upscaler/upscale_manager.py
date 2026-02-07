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
        import urllib.request
        
        # We try both master and main branches to be safe
        branches = ["master", "main"]
        files = ["realesrgan-x4plus.bin", "realesrgan-x4plus.param"]
        
        total_steps = len(files)
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)

        # Add User-Agent to avoid being blocked
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
        urllib.request.install_opener(opener)

        for i, filename in enumerate(files):
            success = False
            last_err = None
            
            for branch in branches:
                url = f"https://raw.githubusercontent.com/xinntao/Real-ESRGAN-ncnn-vulkan/{branch}/models/{filename}"
                target_path = os.path.join(self.model_dir, filename)
                
                try:
                    # Basic downloader with progress
                    def _report(block_num, block_size, total_size):
                        if progress_callback and total_size > 0:
                            file_progress = (block_num * block_size) / total_size
                            overall_progress = int(((i + file_progress) / total_steps) * 100)
                            progress_callback(min(99, overall_progress))

                    urllib.request.urlretrieve(url, target_path, reporthook=_report if progress_callback else None)
                    success = True
                    break # Success with this branch
                except Exception as e:
                    last_err = e
                    continue
            
            if not success:
                print(f"Failed to download {filename} from all known branches: {last_err}")
                raise last_err
        
        if progress_callback:
            progress_callback(100)
