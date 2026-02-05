import sys
import os
import importlib
from PIL import Image


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class EditorCore:

    def __init__(self, max_history=15):
        self.max_history = max_history
        self.history = []
        self.redo_stack = []

        self.filters = self.load_filters()
        self.tools = self.load_tools()
        self.ai_features = self.load_ai_features()

        self.original_image = None          # LAST COMMITTED IMAGE
        self.current_image: Image.Image = None  # PREVIEW / DISPLAY IMAGE
        self.preview_base_image = None
        self.in_preview = False

    # -------------------------
    # Load image
    # -------------------------
    def load_image(self, path):
        img = Image.open(path).convert("RGB")

        self.original_image = img.copy()
        self.current_image = img.copy()

        self.history.clear()
        self.redo_stack.clear()

    # -------------------------
    # Filter Loader
    # -------------------------
    def load_filters(self):
        filters = {}
        filters_path = os.path.join(os.path.dirname(__file__), "filters")

        if not os.path.exists(filters_path):
            # fallback to resource_path for frozen apps
            filters_path = resource_path("editor/filters")
            if not os.path.exists(filters_path):
                return filters

        for file in os.listdir(filters_path):
            if file.endswith(".py") and file != "__init__.py":
                try:
                    module_name = f"editor.filters.{file[:-3]}"
                    module = importlib.import_module(module_name)

                    filter_name = getattr(module, "FILTER_NAME", file[:-3])
                    filters[filter_name] = module
                except Exception as e:
                    print(f"Error loading filter {file}: {e}")

        return filters

    # -------------------------
    # Tool Loader
    # -------------------------
    def load_tools(self):
        tools = {}
        tools_path = os.path.join(os.path.dirname(__file__), "tools")

        if not os.path.exists(tools_path):
            # fallback
            tools_path = resource_path("editor/tools")
            if not os.path.exists(tools_path):
                return tools

        for file in os.listdir(tools_path):
            if file.endswith(".py") and file != "__init__.py":
                try:
                    module_name = f"editor.tools.{file[:-3]}"
                    module = importlib.import_module(module_name)

                    tool_name = getattr(module, "TOOL_NAME", file[:-3])
                    tools[tool_name] = module
                except Exception as e:
                    print(f"Error loading tool {file}: {e}")

        return tools

    # -------------------------
    # AI Feature Loader
    # -------------------------
    def load_ai_features(self):
        features = {}
        ai_path = os.path.join(os.path.dirname(__file__), "ai_features")

        if not os.path.exists(ai_path):
            # fallback
            ai_path = resource_path("editor/ai_features")
            if not os.path.exists(ai_path):
                return features

        for folder in os.listdir(ai_path):
            try:
                dir_path = os.path.join(ai_path, folder)
                if not os.path.isdir(dir_path):
                    continue

                feature_file = os.path.join(dir_path, "feature.py")
                if not os.path.exists(feature_file):
                    continue

                module_name = f"editor.ai_features.{folder}.feature"
                module = importlib.import_module(module_name)

                name = getattr(module, "AI_NAME", folder)
                cls = getattr(module, "AI_CLASS")
                features[name] = cls()
            except Exception as e:
                print(f"Error loading AI feature {folder}: {e}")

        return features

    # =====================================================
    # DESTRUCTIVE FILTERS (BUTTON FILTERS)
    # =====================================================
    def apply_filter(self, name, **kwargs):
        if name not in self.filters or self.original_image is None:
            return False

        # save state
        self.push_history()

        module = self.filters[name]

        if kwargs:
            self.original_image = module.run(self.original_image, **kwargs)
        else:
            self.original_image = module.run(self.original_image)

        self.current_image = self.original_image.copy()
        return True

    def push_history(self):
        if self.original_image:
            self.history.append(self.original_image.copy())
            if len(self.history) > self.max_history:
                self.history.pop(0)
            self.redo_stack.clear()

    # =====================================================
    # PREVIEW (SLIDERS – NON DESTRUCTIVE)
    # =====================================================
    def begin_preview(self):
        if self.original_image:
            # Always preview from last committed base
            self.preview_base_image = self.original_image.copy()
            self.in_preview = True

    def apply_preview_filter(self, name, **kwargs):
        if not self.in_preview or self.preview_base_image is None:
            return False

        module = self.filters[name]
        self.current_image = module.run(self.preview_base_image, **kwargs)
        return True


    def commit_preview(self):
        if not self.in_preview:
            return False

        # save ORIGINAL base, not preview result
        self.push_history()

        # commit preview result as new base
        self.original_image = self.current_image.copy()

        self.preview_base_image = None
        self.in_preview = False
        return True

    # -------------------------
    # Undo / Redo
    # -------------------------
    def undo(self):
        if not self.history:
            return False

        self.redo_stack.append(self.original_image.copy())
        self.original_image = self.history.pop()
        self.current_image = self.original_image.copy()
        return True

    def redo(self):
        if not self.redo_stack:
            return False

        self.history.append(self.original_image.copy())
        self.original_image = self.redo_stack.pop()
        self.current_image = self.original_image.copy()
        return True
