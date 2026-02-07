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
        
        # Correct Raw URL for GitHub
        base_url = "https://raw.githubusercontent.com/xinntao/Real-ESRGAN-ncnn-vulkan/master/models/"
        files = ["realesrgan-x4plus.bin", "realesrgan-x4plus.param"]
        
        total_files = len(files)
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)

        # Add User-Agent to avoid being blocked
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
        urllib.request.install_opener(opener)

        for i, filename in enumerate(files):
            url = base_url + filename
            target_path = os.path.join(self.model_dir, filename)
            
            try:
                # Basic downloader with progress
                def _report(block_num, block_size, total_size):
                    if progress_callback and total_size > 0:
                        # Calculation: (current_file_progress / total_files) + (files_completed / total_files)
                        file_progress = (block_num * block_size) / total_size
                        overall_progress = int(((i + file_progress) / total_files) * 100)
                        progress_callback(min(99, overall_progress))

                urllib.request.urlretrieve(url, target_path, reporthook=_report if progress_callback else None)
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
                raise
        
        if progress_callback:
            progress_callback(100)
