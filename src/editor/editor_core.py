import sys
import os
import importlib
import tempfile
import shutil
import io
import atexit
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
        self.action_log = ["Start"]  # Tracks descriptions of actions
        self.action_index = 0      # Points to current state in action_log

        self.filters = self.load_filters()
        self.tools = self.load_tools()
        self.ai_features = self.load_ai_features()

        self.initial_image = None           # TRUE ORIGINAL (UNEDITED)
        self.original_image = None          # LAST COMMITTED IMAGE (BASE FOR SLIDERS)
        self.current_image: Image.Image = None  # PREVIEW / DISPLAY IMAGE
        self.preview_base_image = None
        self.preview_proxy = None
        self.in_preview = False
        self.current_format = "PNG"         # DEFAULT FORMAT

        # Disk-backed history setup
        self._temp_dir = tempfile.mkdtemp(prefix="painimage_history_")
        self._history_counter = 0
        atexit.register(self._cleanup_temp_dir)

    def _cleanup_temp_dir(self):
        """Cleanup temporary history files."""
        if hasattr(self, "_temp_dir") and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)

    # -------------------------
    # Load image
    # -------------------------
    def load_image(self, path):
        raw_img = Image.open(path)
        # Capture the original format before conversion
        self.current_format = raw_img.format if raw_img.format else "PNG"
        if self.current_format == "MPO": self.current_format = "JPEG" # Handle MPO (3D JPEG)
        
        img = raw_img.convert("RGB")

        self.current_path = path             # STORE CURRENT PATH
        self.initial_image = img.copy()       # Store true original
        self.original_image = img.copy()
        self.current_image = img.copy()

        # Create proxy for smooth previews
        self.preview_proxy = self._create_proxy(self.original_image)

        self.history.clear()
        self.redo_stack.clear()
        
        # Reset action log
        self.action_log = ["Open Image"]
        self.action_index = 0

        # Default state: no slider adjustments
        self._initial_slider_state = {} 
        self._last_size_kb = 0

        # Clear disk history
        if os.path.exists(self._temp_dir):
            for f in os.listdir(self._temp_dir):
                try:
                    os.remove(os.path.join(self._temp_dir, f))
                except OSError:
                    pass

    def save_auto(self):
        """
        Automatically save the current image to the original directory 
        with '_edited' suffix and appropriate extension.
        """
        if not self.current_image or not getattr(self, "current_path", None):
            return None

        # Use the tracked format
        fmt = self.current_format if self.current_format in ["JPEG", "PNG", "WEBP"] else "PNG"
        ext = f".{fmt.lower()}"
        if ext == ".jpeg": ext = ".jpg"

        # Construct new path
        base, _ = os.path.splitext(self.current_path)
        new_path = f"{base}_edited{ext}"

        # Save using the same logic as get_image_info for consistency
        try:
            # We use quality=90 for consistency with estimation logic
            if fmt == "JPEG":
                self.current_image.save(new_path, format="JPEG", quality=90)
            else:
                self.current_image.save(new_path, format=fmt)
            
            return new_path
        except Exception as e:
            print(f"Auto-save failed: {e}")
            return None

    def _create_proxy(self, image):
        """Create a low-res proxy for smooth slider previews."""
        # Target max dimension of 1024px for the proxy (performance sweet spot)
        max_dim = 1024
        w, h = image.size
        if w > max_dim or h > max_dim:
            scale = max_dim / max(w, h)
            # BOX resampling is much faster for downscaling than BILINEAR while maintaining quality
            return image.resize((int(w * scale), int(h * scale)), Image.Resampling.BOX)
        return image.copy()

    def _save_to_temp(self, image):
        """Save a PIL image to temp disk and return path."""
        self._history_counter += 1
        path = os.path.join(self._temp_dir, f"state_{self._history_counter}.png")
        image.save(path, format="PNG")
        return path

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

        # Build-in push history for destructive filters
        self.push_history(description=name)

        module = self.filters[name]

        if kwargs:
            self.original_image = module.run(self.original_image, **kwargs)
        else:
            self.original_image = module.run(self.original_image)

        self.current_image = self.original_image.copy()
        # Update proxy after destructive change
        self.preview_proxy = self._create_proxy(self.original_image)
        return True

    def apply_baked_filter(self, filter_list, slider_state, filter_name, **kwargs):
        """
        Helper to bake current sliders AND apply a new filter in one go.
        Useful for running in a background thread to avoid GUI lag.
        """
        # 1. Bake
        if filter_list:
            self.commit_preview(filter_list, slider_state)
        
        # 2. Apply new filter
        return self.apply_filter(filter_name, **kwargs)

    def apply_tool(self, name, **kwargs):
        """Apply a tool to the current image and update state."""
        if name not in self.tools or self.original_image is None:
            return None

        # Tools are destructive to the current workflow state (they push history)
        self.push_history(description=name)

        module = self.tools[name]
        result = module.run(self.current_image.copy(), **kwargs)

        if result is not None:
            # Capture the format if the tool set it (primarily for Convert)
            if hasattr(result, "format") and result.format:
                self.current_format = result.format
                
            self.original_image = result.copy()
            self.current_image = self.original_image.copy()
            # Update proxy after tool application
            self.preview_proxy = self._create_proxy(self.original_image)
            return self.current_image
        
        return None

    def push_history(self, slider_state=None, description="Edit"):
        if self.original_image:
            # Save image to disk instead of memory
            path = self._save_to_temp(self.original_image)
            state = (path, slider_state.copy() if slider_state else {})
            self.history.append(state)
            
            if len(self.history) > self.max_history:
                old_path, _ = self.history.pop(0)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Clear redo stack and its files
            for old_redo_path, _ in self.redo_stack:
                if os.path.exists(old_redo_path):
                    try:
                        os.remove(old_redo_path)
                    except OSError:
                        pass
            self.redo_stack.clear()
            
            # Update action log
            # Truncate any 'redo' actions that are now invalid
            self.action_log = self.action_log[:self.action_index + 1]
            self.action_log.append(description)
            self.action_index += 1
            
            # Maintain log size consistent with history size
            if len(self.action_log) > self.max_history + 1: # +1 for initial state
                self.action_log.pop(0)
                self.action_index -= 1

    # =====================================================
    # PREVIEW (SLIDERS – NON DESTRUCTIVE)
    # =====================================================
    def apply_preview_filter(self, name, **kwargs):
        """Single preview filter application on PROXY."""
        if not self.in_preview or self.preview_proxy is None:
            return False

        module = self.filters[name]
        self.current_image = module.run(self.preview_proxy.copy(), **kwargs)
        return True

    def apply_preview_filters(self, filter_list):
        """Apply multiple preview filters in a chain starting from proxy."""
        if not self.in_preview or self.preview_proxy is None:
            return False
            
        img = self.preview_proxy.copy()
        for name, kwargs in filter_list:
            if name in self.filters:
                img = self.filters[name].run(img, **kwargs)
        
        self.current_image = img
        return True

    def commit_preview(self, filter_list=None, slider_state=None, description="Apply Adjustments"):
        """Permanently apply current preview state to history."""
        if not self.in_preview or self.original_image is None:
            return False
            
        # Re-apply filters to FULL RESOLUTION image before commit
        if filter_list:
            img = self.original_image.copy()
            for name, kwargs in filter_list:
                if name in self.filters:
                    img = self.filters[name].run(img, **kwargs)
            self.push_history(slider_state, description=description)
            self.original_image = img
        else:
            self.push_history(slider_state, description=description)
            self.original_image = self.current_image.copy()

        self.current_image = self.original_image.copy()
        self.preview_proxy = self._create_proxy(self.original_image)
        self.in_preview = False
        return True

    # -------------------------
    # Undo / Redo
    # -------------------------
    def undo(self, current_slider_state=None):
        if not self.history:
            return None

        # Save current state to redo stack
        path = self._save_to_temp(self.original_image)
        current_state = (path, current_slider_state.copy() if current_slider_state else {})
        self.redo_stack.append(current_state)

        # Restore previous state from disk
        path, slider_state = self.history.pop()
        image = Image.open(path)
        self.original_image = image.copy()
        self.current_image = image.copy()
        image.close()
        # Regenerate proxy so sliders apply to the correct base
        self.preview_proxy = self._create_proxy(self.original_image)

        self.action_index -= 1
        return slider_state

    def redo(self, current_slider_state=None):
        if not self.redo_stack:
            return None

        # Save current state to history
        path = self._save_to_temp(self.original_image)
        current_state = (path, current_slider_state.copy() if current_slider_state else {})
        self.history.append(current_state)

        # Restore next state from disk
        path, slider_state = self.redo_stack.pop()
        image = Image.open(path)
        self.original_image = image.copy()
        self.current_image = image.copy()
        image.close()
        # Regenerate proxy so sliders apply to the correct base
        self.preview_proxy = self._create_proxy(self.original_image)

        self.action_index += 1
        return slider_state

    def get_image_info(self, estimate_size=False):
        """Return basic info about the current image."""
        if self.current_image is None:
            return None
        
        info = {
            "width": self.current_image.width,
            "height": self.current_image.height,
            "format": self.current_format,
            "mode": self.current_image.mode,
            "size_kb": getattr(self, "_last_size_kb", 0)
        }

        if estimate_size:
            # Estimate size if possible - EXPENSIVE OPERATION
            try:
                buffer = io.BytesIO()
                fmt = info["format"] if info["format"] in ["JPEG", "PNG", "WEBP"] else "PNG"
                if fmt == "JPEG":
                    self.current_image.save(buffer, format="JPEG", quality=90)
                else:
                    self.current_image.save(buffer, format=fmt)
                info["size_kb"] = buffer.getbuffer().nbytes // 1024
                self._last_size_kb = info["size_kb"]
            except:
                pass
            
        return info
