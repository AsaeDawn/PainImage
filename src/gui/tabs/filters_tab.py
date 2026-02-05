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

        # Track active slider values
        self.slider_values = {}
        self.slider_widgets = {}

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
                # Auto-save history when slider is released
                slider.sliderReleased.connect(self.commit_to_history)

                self.vbox.addWidget(slider)
                self.slider_widgets[name] = slider

            # ---------- SIMPLE FILTER ----------
            else:
                btn = QPushButton(name)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                btn.clicked.connect(
                    lambda checked=False, n=name: self.apply_simple_filter(n)
                )
                self.vbox.addWidget(btn)

        self.vbox.addStretch(1)
        scroll.setWidget(container)
        layout.addWidget(scroll)

    # -------------------------
    def apply_simple_filter(self, name):
        # Commit current slider state to history BEFORE applying a new filter
        self.core.push_history(self.slider_values)
        self.core.apply_filter(name)
        # Re-apply current slider values to the NEW filtered base
        self.apply_combined_filters()

    def commit_to_history(self):
        """Save the current visual state to undo history."""
        self.core.push_history(self.slider_values)

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
        self.set_slider_state({name: 50 for name in self.slider_values})

    def set_slider_state(self, state):
        """Update slider positions from a dictionary without triggering new calculations."""
        self.slider_values = state.copy()
        
        for name, slider in self.slider_widgets.items():
            val = state.get(name, 50)
            slider.blockSignals(True)
            slider.setValue(val)
            slider.blockSignals(False)
        
        # update display based on restored state
        self.apply_combined_filters()
