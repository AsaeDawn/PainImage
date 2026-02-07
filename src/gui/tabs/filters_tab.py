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
        self.slider_state_before_move = {}

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
                
                # Add tick marks
                slider.setTickPosition(QSlider.TicksBelow)
                slider.setTickInterval(25)

                slider.valueChanged.connect(
                    lambda value, n=name: self.on_slider_changed(n, value)
                )
                
                # Undo tracking: capture state BEFORE move starts
                slider.sliderPressed.connect(self.capture_before_move)
                # Auto-save history when slider is released + trigger full preview update (with size)
                slider.sliderReleased.connect(self.on_slider_released)

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
        # Background task for destructive filter
        def _on_finished(ok):
            self.apply_combined_filters()
            self.window().refresh_preview()

        # Get active sliders
        active_filters = self.get_active_filters()
        
        # We always reset sliders locally immediately for visual feedback
        # The background task will handle the actual commitment of those values.
        saved_slider_values = self.slider_values.copy()
        if active_filters:
            self.reset_all_sliders()

        self.window().run_background_task(
            self.core.apply_baked_filter,
            args=[active_filters, saved_slider_values, name],
            on_finished=_on_finished,
            msg=f"Applying {name}..."
        )

    def capture_before_move(self):
        """Store the current positions before a new adjustment starts."""
        self.slider_state_before_move = self.slider_values.copy()


    def get_active_filters(self):
        """Build the list of active filters with their current slider values."""
        filter_list = []
        for name, value in self.slider_values.items():
            if value != 50:
                delta = (value - 50) * 2
                filter_list.append((name, {"delta": delta}))
        return filter_list

    def on_slider_released(self):
        """Handle slider release: save state to history without 'baking' into base."""
        self.core.push_history(self.slider_values)
        
        try:
            self.window().refresh_preview(estimate_size=True)
        except:
            pass

    def on_slider_changed(self, name, value):
        self.slider_values[name] = value
        self.apply_combined_filters()

    def apply_combined_filters(self):
        """Apply all active sliders to the current base image."""
        self.core.in_preview = True # Ensure preview mode is active
        
        filter_list = self.get_active_filters()
        
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
