from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea, QWidget, QSizePolicy, QInputDialog

class ToolsTab(QWidget):
    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6,6,6,6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(8)

        # List available tools (if any)
        for name in sorted(self.core.tools.keys()):
            btn = QPushButton(name)
            btn.clicked.connect(self.make_tool(name))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            vbox.addWidget(btn)

        vbox.addStretch(1)
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def make_tool(self, name):
        def _do():
            # Resize dialog example expects two ints
            if name == "Resize Image":
                w, ok = QInputDialog.getInt(self, "Resize", "Width:", min=1, value=800)
                if not ok: return
                h, ok = QInputDialog.getInt(self, "Resize", "Height:", min=1, value=600)
                if not ok: return
                self.core.push_history()
                self.core.tools[name](self.core.current_image, w, h)
                try:
                    self.parent().parent().refresh_preview()
                except: pass
            elif name == "Compress to Size":
                kb, ok = QInputDialog.getInt(self, "Compress", "Target KB:", min=1, value=100)
                if not ok: return
                self.core.push_history()
                self.core.current_image = self.core.tools[name](self.core.current_image, kb)
                try:
                    self.parent().parent().refresh_preview()
                except: pass
            elif name == "Convert Format":
                # For convert we will just set format info - actual saving will convert.
                fmt, ok = QInputDialog.getItem(self, "Convert", "Format:", ["PNG","JPEG","WEBP"], 0, False)
                if not ok: return
                self.core.push_history()
                self.core.current_image = self.core.tools[name](self.core.current_image, fmt)
                try:
                    self.parent().parent().refresh_preview()
                except: pass
            else:
                # generic call
                self.core.push_history()
                res = self.core.tools[name](self.core.current_image)
                if res is not None:
                    self.core.current_image = res
                try:
                    self.parent().parent().refresh_preview()
                except: pass
        return _do
