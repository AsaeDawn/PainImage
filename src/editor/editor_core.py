import os
import importlib
from PIL import Image


class EditorCore:

    def __init__(self):
        self.current_image: Image.Image = None
        self.filters = self.load_filters()

    # -------------------------
    # Load image
    # -------------------------
    def load_image(self, path):
        self.current_image = Image.open(path)

    # -------------------------
    # Dynamic filter loader
    # -------------------------
    def load_filters(self):
        filters = {}

        filters_path = os.path.join(os.path.dirname(__file__), "filters")

        for file in os.listdir(filters_path):
            if file.endswith(".py") and file not in ["__init__.py"]:
                module_name = f"editor.filters.{file[:-3]}"
                module = importlib.import_module(module_name)

                filter_name = getattr(module, "FILTER_NAME", file[:-3])
                filter_func = getattr(module, "run")

                filters[filter_name] = filter_func

        return filters

    # -------------------------
    # Apply filter by name
    # -------------------------
    def apply_filter(self, name):
        if name in self.filters:
            self.current_image = self.filters[name](self.current_image)
            return True
        return False
