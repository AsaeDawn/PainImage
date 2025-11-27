import os
import importlib
from PIL import Image


class EditorCore:

    def __init__(self):
        self.current_image: Image.Image = None
        self.history = [] 
        self.redo_stack = []
        # Load filters and tools
        self.filters = self.load_filters()
        self.tools = self.load_tools()   
        self.original_image = None
        self.current_image = None


    # -------------------------
    # Load image
    # -------------------------
    def load_image(self, path):
        img = Image.open(path)
        self.original_image = img.copy()      # <-- store original
        self.current_image = img.copy()       # <-- working copy
        self.history = []
        self.redo_stack = []

    # -------------------------
    # Filter Loader
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
    # Tool Loader  (NEW)
    # -------------------------
    def load_tools(self):
        tools = {}

        tools_path = os.path.join(os.path.dirname(__file__), "tools")

        if not os.path.exists(tools_path):
            return tools  # No tools yet

        for file in os.listdir(tools_path):
            if file.endswith(".py") and file not in ["__init__.py"]:
                module_name = f"editor.tools.{file[:-3]}"
                module = importlib.import_module(module_name)

                tool_name = getattr(module, "TOOL_NAME", file[:-3])
                tool_func = getattr(module, "run")

                tools[tool_name] = tool_func

        return tools

    # -------------------------
    # Apply filter by name
    # -------------------------
    def apply_filter(self, name):
        if name in self.filters:
            self.push_history()  
            self.current_image = self.filters[name](self.current_image)
            return True
        return False

    def push_history(self):
        if self.current_image:
            self.history.append(self.current_image.copy())
            # applying new action clears redo history
            self.redo_stack.clear()

    def undo(self):
        if not self.history:
            return False

        # move current to redo stack
        self.redo_stack.append(self.current_image.copy())

        # restore last history
        self.current_image = self.history.pop()
        return True

    def redo(self):
        if not self.redo_stack:
            return False

        # push current state to undo history
        self.history.append(self.current_image.copy())

        # restore from redo
        self.current_image = self.redo_stack.pop()
        return True
