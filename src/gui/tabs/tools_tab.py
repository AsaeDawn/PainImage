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
            res = None
            if name == "Resize Image":
                w, ok = QInputDialog.getInt(self, "Resize", "Width:", 800, 1)
                if not ok: return
                h, ok = QInputDialog.getInt(self, "Resize", "Height:", 600, 1)
                if not ok: return
                res = self.core.apply_tool(name, width=w, height=h)

            elif name == "Compress to Size":
                kb, ok = QInputDialog.getInt(self, "Compress", "Target KB:", 100, 1)
                if not ok: return
                res = self.core.apply_tool(name, target_kb=kb)

            elif name == "Convert Format":
                fmt, ok = QInputDialog.getItem(self, "Convert", "Format:", ["PNG","JPEG","WEBP"], 0, False)
                if not ok: return
                res = self.core.apply_tool(name, fmt=fmt)

            else:
                # generic call
                res = self.core.apply_tool(name)

            if res is not None:
                try:
                    # In main_window, SideBar is a child of MainWindow's central widget or sidebar
                    # Usually we want to find the MainWindow or just call a refresh.
                    # Based on existing code: self.parent().parent().refresh_preview()
                    self.window().refresh_preview(estimate_size=True)
                except:
                    pass
        return _do
