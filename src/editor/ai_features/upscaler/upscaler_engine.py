import subprocess
import os
import tempfile
from PIL import Image

class UpscalerEngine:
    def __init__(self, model_dir):
        """
        model_dir must contain:
            realesrgan-ncnn-vulkan (extension depends on OS)
            realesrgan-x4plus.bin
            realesrgan-x4plus.param
        """
        self.model_dir = model_dir
        import sys
        binary_name = "realesrgan-ncnn-vulkan"
        if sys.platform == "win32":
            binary_name += ".exe"
        self.binary = os.path.join(model_dir, binary_name)

    def upscale(self, pil_image: Image.Image):
        # 1. Verify models exist before starting
        import sys
        binary_name = "realesrgan-ncnn-vulkan"
        if sys.platform == "win32":
            binary_name += ".exe"
            
        required_files = [
            binary_name,
            "realesrgan-x4plus.bin",
            "realesrgan-x4plus.param"
        ]
        for f in required_files:
            if not os.path.exists(os.path.join(self.model_dir, f)):
                raise FileNotFoundError(f"Missing required AI file: {f}. Please click 'Download' in the AI tab.")

        # Create a temporary directory that will be deleted automatically
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, "upscale_input.png")
            output_path = os.path.join(tmp_dir, "upscale_output.png")

            # Save image to disk (NCNN works with file paths)
            pil_image.save(input_path)

            # Ensure binary is executable (on Linux this might not be needed but kept for portability)
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
                "-m", self.model_dir,
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
