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
            # Get current active adjustments to bake
            active_filters = self.window().sidebar.filters_tab.get_active_filters()
            slider_values = self.window().sidebar.filters_tab.slider_values.copy()

            def _on_tool_finished(res):
                if res:
                    self.window().sidebar.filters_tab.reset_all_sliders()
                    self.window().refresh_preview()

            if name == "Resize Image":
                info = self.core.get_image_info()
                curr_w = info["width"] if info else 800
                curr_h = info["height"] if info else 600
                
                dlg = ResizeDialog(curr_w, curr_h, self)
                if dlg.exec() == QDialog.Accepted:
                    w, h = dlg.get_values()
                    
                    def _task():
                        if active_filters:
                            self.core.commit_preview(active_filters, slider_values)
                        return self.core.apply_tool(name, width=w, height=h)

                    self.window().run_background_task(
                        _task,
                        on_finished=_on_tool_finished,
                        msg=f"Resizing to {w}x{h}..."
                    )

            elif name == "Compress to Size":
                kb, ok = QInputDialog.getInt(self, "Compress", "Target KB:", 100, 1)
                if not ok: return

                def _task():
                    if active_filters:
                        self.core.commit_preview(active_filters, slider_values)
                    return self.core.apply_tool(name, target_kb=kb)

                self.window().run_background_task(
                    _task,
                    on_finished=_on_tool_finished,
                    msg=f"Compressing to {kb} KB..."
                )

            elif name == "Convert Format":
                fmt, ok = QInputDialog.getItem(self, "Convert", "Format:", ["PNG","JPEG","WEBP"], 0, False)
                if not ok: return
                
                def _on_convert_finished(res):
                    if res:
                        self.window().sidebar.filters_tab.reset_all_sliders()
                        saved_path = self.core.save_auto()
                        if saved_path:
                            try: self.window().statusBar().showMessage(f"Saved to: {saved_path}", 5000)
                            except Exception: pass
                        self.window().refresh_preview()

                def _task():
                    if active_filters:
                        self.core.commit_preview(active_filters, slider_values)
                    return self.core.apply_tool(name, fmt=fmt)

                self.window().run_background_task(
                    _task,
                    on_finished=_on_convert_finished,
                    msg=f"Converting to {fmt}..."
                )

            else:
                def _task():
                    if active_filters:
                        self.core.commit_preview(active_filters, slider_values)
                    return self.core.apply_tool(name)

                self.window().run_background_task(
                    _task,
                    on_finished=_on_tool_finished,
                    msg=f"Applying tool: {name}..."
                )
        return _do
