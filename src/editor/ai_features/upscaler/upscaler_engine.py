import subprocess
import os
import sys
import tempfile
from PIL import Image

class UpscalerEngine:
    def __init__(self, model_dir):
        """
        model_dir layout:
            windows/realesrgan-ncnn-vulkan.exe   (Windows binary)
            linux/realesrgan-ncnn-vulkan          (Linux binary)
            models/realesrgan-x4plus.bin
            models/realesrgan-x4plus.param
        """
        self.model_dir = model_dir
        self.models_dir = os.path.join(model_dir, "models")

        # Resolve platform-specific binary
        if sys.platform == "win32":
            self.binary = os.path.join(model_dir, "windows", "realesrgan-ncnn-vulkan.exe")
        else:
            self.binary = os.path.join(model_dir, "linux", "realesrgan-ncnn-vulkan")

    def upscale(self, pil_image: Image.Image):
        # 1. Verify required files exist
        if not os.path.exists(self.binary):
            raise FileNotFoundError(f"Missing AI binary: {self.binary}")

        required_models = [
            "realesrgan-x4plus.bin",
            "realesrgan-x4plus.param"
        ]
        for f in required_models:
            path = os.path.join(self.models_dir, f)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing required AI model file: {f}")

        # Create a temporary directory that will be deleted automatically
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, "upscale_input.png")
            output_path = os.path.join(tmp_dir, "upscale_output.png")

            # Save image to disk (NCNN works with file paths)
            pil_image.save(input_path)

            # Ensure binary is executable (needed on Linux)
            if not os.access(self.binary, os.X_OK):
                try:
                    os.chmod(self.binary, 0o755)
                except:
                    pass

            # NCNN REAL ESRGAN COMMAND
            cmd = [
                self.binary,
                "-i", input_path,
                "-o", output_path,
                "-n", "realesrgan-x4plus",
                "-s", "4",
                "-t", "400",
                "-m", self.models_dir,
            ]

            try:
                # Run the binary
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                # Capture stderr for better debugging
                error_msg = e.stderr if e.stderr else str(e)
                raise RuntimeError(f"AI Engine failed: {error_msg}")

            # Load the upscaled image back into PIL and make a copy to free the file handle
            if not os.path.exists(output_path):
                raise RuntimeError("AI Engine finished but output file was not created.")

            with Image.open(output_path) as res_img:
                return res_img.copy()
