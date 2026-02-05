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

        self.initial_image = None           # TRUE ORIGINAL (UNEDITED)
        self.original_image = None          # LAST COMMITTED IMAGE (BASE FOR SLIDERS)
        self.current_image: Image.Image = None  # PREVIEW / DISPLAY IMAGE
        self.preview_base_image = None
        self.in_preview = False

    # -------------------------
    # Load image
    # -------------------------
    def load_image(self, path):
        img = Image.open(path).convert("RGB")

        self.initial_image = img.copy()       # Store true original
        self.original_image = img.copy()
        self.current_image = img.copy()

        self.history.clear()
        self.redo_stack.clear()
        # Default state: no slider adjustments
        self._initial_slider_state = {} 

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

    def push_history(self, slider_state=None):
        if self.original_image:
            # Store image and the state of sliders *at that moment*
            state = (self.original_image.copy(), slider_state.copy() if slider_state else {})
            self.history.append(state)
            if len(self.history) > self.max_history:
                self.history.pop(0)
            self.redo_stack.clear()

    # =====================================================
    # PREVIEW (SLIDERS – NON DESTRUCTIVE)
    # =====================================================
    def apply_preview_filter(self, name, **kwargs):
        """Single preview filter application."""
        if not self.in_preview or self.original_image is None:
            return False

        module = self.filters[name]
        self.current_image = module.run(self.original_image, **kwargs)
        return True

    def apply_preview_filters(self, filter_list):
        """Apply multiple preview filters in a chain starting from original_image."""
        if not self.in_preview or self.original_image is None:
            return False
            
        img = self.original_image.copy()
        for name, kwargs in filter_list:
            if name in self.filters:
                img = self.filters[name].run(img, **kwargs)
        
        self.current_image = img
        return True

    def commit_preview(self):
        """Permanently apply current preview state to history."""
        if not self.in_preview or self.current_image is None:
            return False

        self.push_history()
        self.original_image = self.current_image.copy()
        # Preview stays active but base defaults to new original if we wanted, 
        # but for simple sliders we usually stop preview after commit.
        self.in_preview = False
        return True

    # -------------------------
    # Undo / Redo
    # -------------------------
    def undo(self, current_slider_state=None):
        if not self.history:
            return None

        # Save current state to redo stack before moving back
        current_state = (self.original_image.copy(), current_slider_state.copy() if current_slider_state else {})
        self.redo_stack.append(current_state)

        # Restore previous state
        image, slider_state = self.history.pop()
        self.original_image = image.copy()
        self.current_image = image.copy()

        return slider_state

    def redo(self, current_slider_state=None):
        if not self.redo_stack:
            return None

        # Save current state to history before moving forward
        current_state = (self.original_image.copy(), current_slider_state.copy() if current_slider_state else {})
        self.history.append(current_state)

        # Restore next state
        image, slider_state = self.redo_stack.pop()
        self.original_image = image.copy()
        self.current_image = image.copy()

        return slider_state
