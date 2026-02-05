from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QPushButton,
    QSizePolicy,
    QLabel,
    QSlider
)
from PySide6.QtCore import Signal, Qt


class FiltersTab(QWidget):
    filter_applied = Signal()

    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        self.vbox = QVBoxLayout(container)
        self.vbox.setSpacing(10)

        # Track active slider values (default 50 = neutral for both Brightness and Contrast)
        self.slider_values = {}

        for name in sorted(self.core.filters.keys()):
            filter_obj = self.core.filters[name]

            # ---------- PARAMETER FILTER (e.g. Brightness, Contrast) ----------
            if getattr(filter_obj, "HAS_PARAMS", False):
                self.slider_values[name] = 50  # default neutral

                label = QLabel(name)
                label.setStyleSheet("font-weight: bold;")
                self.vbox.addWidget(label)

                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(0)
                slider.setMaximum(100)
                slider.setValue(50) 
                slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                slider.valueChanged.connect(
                    lambda value, n=name: self.on_slider_changed(n, value)
                )

                self.vbox.addWidget(slider)

            # ---------- SIMPLE FILTER ----------
            else:
                btn = QPushButton(name)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                btn.clicked.connect(
                    lambda checked=False, n=name: self.apply_simple_filter(n)
                )
                self.vbox.addWidget(btn)

        # Add Apply button for sliders
        self.apply_btn = QPushButton("Apply Slider Changes")
        self.apply_btn.setObjectName("apply_sliders_btn")
        self.apply_btn.clicked.connect(self.commit_sliders)
        self.vbox.addWidget(self.apply_btn)

        self.vbox.addStretch(1)
        scroll.setWidget(container)
        layout.addWidget(scroll)

    # -------------------------
    # Filter handlers
    # -------------------------
    def apply_simple_filter(self, name):
        # Don't bake sliders into this action, just apply the filter to the base
        self.core.apply_filter(name)
        # Re-apply the current slider positions on top of the new base image
        self.apply_combined_filters()

    def commit_sliders(self):
        if self.core.in_preview:
            self.core.commit_preview()
            self.reset_all_sliders()
            self.filter_applied.emit()

    def on_slider_changed(self, name, value):
        self.slider_values[name] = value
        self.apply_combined_filters()

    def apply_combined_filters(self):
        """Apply all active sliders to the current base image."""
        self.core.in_preview = True # Ensure preview mode is active
        
        filter_list = []
        for name, value in self.slider_values.items():
            if value != 50:
                delta = (value - 50) * 2
                filter_list.append((name, {"delta": delta}))
        
        # If no sliders are active, just show original base
        if not filter_list:
            self.core.current_image = self.core.original_image.copy()
        else:
            self.core.apply_preview_filters(filter_list)
        
        self.filter_applied.emit()

    def reset_all_sliders(self):
        # Visually reset sliders without triggering double processing if possible
        self.slider_values = {name: 50 for name in self.slider_values}
        # Find all sliders in layout and set to 50
        for i in range(self.vbox.count()):
            widget = self.vbox.itemAt(i).widget()
            if isinstance(widget, QSlider):
                widget.blockSignals(True)
                widget.setValue(50)
                widget.blockSignals(False)
