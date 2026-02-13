from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, 
    QSizePolicy, QInputDialog, QDialog, QFormLayout, 
    QSpinBox, QDialogButtonBox, QComboBox, QHBoxLayout, QLabel, QStackedWidget
)
from PySide6.QtCore import Qt

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

class CropPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        layout.addWidget(QLabel("<b>Crop Image</b>"))
        
        # Ratio
        layout.addWidget(QLabel("Aspect Ratio:"))
        self.ratio_combo = QComboBox()
        self.ratio_combo.addItems(["Free", "Original", "1:1", "4:3", "16:9", "3:4", "9:16"])
        layout.addWidget(self.ratio_combo)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()

class ToolsTab(QWidget):
    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        # Stack to switch between List and Crop Panel
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Page 1: Tool List
        self.tool_list_page = QWidget()
        list_layout = QVBoxLayout(self.tool_list_page)
        list_layout.setContentsMargins(6,6,6,6)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(8)

        # List available tools (if any)
        # We manually add "Crop Image" if not present in core.tools? 
        # Or assume it is there. If "Crop Image " is a Tool (crop.py), it should be in core.tools.
        # But we need to handle it specially.
        
        tool_names = sorted(list(self.core.tools.keys()))
        if "Crop Image" not in tool_names:
             # If crop.py exists it should be there. 
             # If I created it properly, it should be loaded.
             pass

        for name in tool_names:
            btn = QPushButton(name)
            btn.clicked.connect(self.make_tool(name))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            vbox.addWidget(btn)

        vbox.addStretch(1)
        scroll.setWidget(container)
        list_layout.addWidget(scroll)
        
        self.stack.addWidget(self.tool_list_page)

        # Page 2: Crop Panel
        self.crop_panel = CropPanel()
        self.crop_panel.apply_btn.clicked.connect(self.on_crop_apply)
        self.crop_panel.cancel_btn.clicked.connect(self.on_crop_cancel)
        self.crop_panel.ratio_combo.currentTextChanged.connect(self.on_crop_ratio_changed)
        
        self.stack.addWidget(self.crop_panel)

    def make_tool(self, name):
        def _do():
            if name == "Crop Image":
                self.start_crop_mode()
                return

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

    # --- Crop Mode Handling ---

    def start_crop_mode(self):
        # 1. Switch UI
        self.stack.setCurrentWidget(self.crop_panel)
        # 2. Tell ImageView to show CropItem
        self.window().image_view.start_crop()
        
    def on_crop_cancel(self):
        # 1. Revert UI
        self.stack.setCurrentWidget(self.tool_list_page)
        # 2. Tell ImageView to hide CropItem
        self.window().image_view.end_crop()

    def on_crop_ratio_changed(self, text):
        ratio = None
        if text == "1:1": ratio = 1.0
        elif text == "4:3": ratio = 4/3
        elif text == "16:9": ratio = 16/9
        elif text == "3:4": ratio = 3/4
        elif text == "9:16": ratio = 9/16
        elif text == "Original":
             info = self.core.get_image_info()
             if info and info['height'] > 0:
                 ratio = info['width'] / info['height']
        
        self.window().image_view.set_crop_ratio(ratio)

    def on_crop_apply(self):
        # 1. Get Crop Box from View
        box = self.window().image_view.get_crop_box()
        # box is (left, top, right, bottom)
        
        if not box:
            self.on_crop_cancel()
            return
            
        # 2. Apply via Core
        active_filters = self.window().sidebar.filters_tab.get_active_filters()
        slider_values = self.window().sidebar.filters_tab.slider_values.copy()
        
        def _task():
            if active_filters:
                self.core.commit_preview(active_filters, slider_values)
            return self.core.apply_tool("Crop Image", box=box)

        def _on_finished(res):
            self.on_crop_cancel() # Exit crop mode logic
            if res:
                self.window().sidebar.filters_tab.reset_all_sliders()
                self.window().refresh_preview()

        self.window().run_background_task(
            _task, 
            on_finished=_on_finished,
            msg="Cropping..."
        )
