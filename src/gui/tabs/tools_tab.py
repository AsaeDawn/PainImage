from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, 
    QSizePolicy, QInputDialog, QDialog, QFormLayout, 
    QSpinBox, QDialogButtonBox
)

class ResizeDialog(QDialog):
    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resize Image")
        layout = QFormLayout(self)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(width)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(height)

        layout.addRow("Width:", self.width_spin)
        layout.addRow("Height:", self.height_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_values(self):
        return self.width_spin.value(), self.height_spin.value()

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
            if name == "Resize Image":
                # Get current resolution for defaults
                info = self.core.get_image_info()
                curr_w = info["width"] if info else 800
                curr_h = info["height"] if info else 600
                
                dlg = ResizeDialog(curr_w, curr_h, self)
                if dlg.exec() == QDialog.Accepted:
                    w, h = dlg.get_values()
                    self.window().run_background_task(
                        self.core.apply_tool, 
                        args=[name], 
                        kwargs={"width": w, "height": h},
                        msg=f"Resizing to {w}x{h}..."
                    )

            elif name == "Compress to Size":
                kb, ok = QInputDialog.getInt(self, "Compress", "Target KB:", 100, 1)
                if not ok: return
                self.window().run_background_task(
                    self.core.apply_tool,
                    args=[name],
                    kwargs={"target_kb": kb},
                    msg=f"Compressing to {kb} KB..."
                )

            elif name == "Convert Format":
                fmt, ok = QInputDialog.getItem(self, "Convert", "Format:", ["PNG","JPEG","WEBP"], 0, False)
                if not ok: return
                
                def _on_convert_finished(res):
                    if res:
                        # Automatically save in original directory
                        saved_path = self.core.save_auto()
                        if saved_path:
                            try:
                                self.window().statusBar().showMessage(f"Saved to: {saved_path}", 5000)
                            except: pass
                        self.window().refresh_preview(estimate_size=True)

                self.window().run_background_task(
                    self.core.apply_tool,
                    args=[name],
                    kwargs={"fmt": fmt},
                    on_finished=_on_convert_finished,
                    msg=f"Converting to {fmt}..."
                )

            else:
                # generic tool call
                self.window().run_background_task(
                    self.core.apply_tool,
                    args=[name],
                    msg=f"Applying tool: {name}..."
                )
        return _do
