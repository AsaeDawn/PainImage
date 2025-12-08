import subprocess
import os
from PIL import Image

class UpscalerEngine:
    def __init__(self, model_dir):
        """
        model_dir must contain:
            realesrgan-ncnn-vulkan  (binary)
            realesrgan-x4.bin
            realesrgan-x4.param
        """
        self.model_dir = model_dir
        self.binary = os.path.join(model_dir, "realesrgan-ncnn-vulkan")

    def upscale(self, pil_image: Image.Image):
        # Temporary file paths
        input_path = "/tmp/upscale_input.png"
        output_path = "/tmp/upscale_output.png"

        # Save image to disk (NCNN works with file paths)
        pil_image.save(input_path)

        # Ensure binary is executable
        if not os.access(self.binary, os.X_OK):
            os.chmod(self.binary, 0o755)

        # NCNN REAL ESRGAN COMMAND
        cmd = [
            self.binary,
            "-i", input_path,
            "-o", output_path,
            "-n", "realesrgan-x4plus",   # must use one of supported names
            "-s", "4",
            "-t", "400",                 # tile size (default 0 = auto)
            "-m", self.model_dir,
        ]

        # Run the binary (errors raise exceptions)
        subprocess.run(cmd, check=True)

        # Load the upscaled image back into PIL
        return Image.open(output_path)
