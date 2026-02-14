from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QSizePolicy,
    QLabel,
    QSlider,
    QGroupBox
)
from PySide6.QtCore import Signal, Qt
import copy

class ColorsTab(QWidget):
    filter_applied = Signal()

    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        container = QWidget()
        self.vbox = QVBoxLayout(container)
        self.vbox.setSpacing(15)
        self.vbox.setContentsMargins(10, 10, 10, 10)

        # Track active slider values
        # Structure: { filter_name: { param_name: value } }
        self.slider_values = {}
        # Structure: { filter_name: { param_name: widget } }
        self.slider_widgets = {}
        
        # State tracking for undo/redo
        self.slider_state_before_move = {}

        # Collect Parametric Filters
        param_filters = []
        for name in sorted(self.core.filters.keys()):
            filter_obj = self.core.filters[name]
            if getattr(filter_obj, "HAS_PARAMS", False):
                param_filters.append(name)

        # Build UI
        for name in param_filters:
            filter_obj = self.core.filters[name]
            params = getattr(filter_obj, "PARAMS", {})
            
            group = QGroupBox(name)
            group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
            group_layout = QVBoxLayout(group)
            
            self.slider_values[name] = {}
            self.slider_widgets[name] = {}

            for param_key, param_info in params.items():
                min_val = param_info.get("min", 0)
                max_val = param_info.get("max", 100)
                default_val = param_info.get("default", 0)
                label_text = param_info.get("label", param_key.capitalize())

                self.slider_values[name][param_key] = default_val

                row_layout = QVBoxLayout()
                lbl = QLabel(label_text)
                lbl.setStyleSheet("color: #555; font-size: 11px;")
                
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(min_val)
                slider.setMaximum(max_val)
                slider.setValue(default_val)
                slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
                slider.valueChanged.connect(
                    lambda value, n=name, k=param_key: self.on_slider_changed(n, k, value)
                )
                slider.sliderPressed.connect(self.capture_before_move)
                slider.sliderReleased.connect(
                    lambda n=name: self.on_slider_released(n)
                )

                self.slider_widgets[name][param_key] = slider
                
                row_layout.addWidget(lbl)
                row_layout.addWidget(slider)
                group_layout.addLayout(row_layout)
            
            self.vbox.addWidget(group)

        self.vbox.addStretch(1)
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def capture_before_move(self):
        """Store the current positions before a new adjustment starts."""
        self.slider_state_before_move = copy.deepcopy(self.slider_values)

    def get_active_filters(self):
        """
        Build the list of active filters with their current slider values.
        Returns list of (filter_name, kwargs_dict)
        """
        filter_list = []
        for name, params_dict in self.slider_values.items():
            is_active = False
            filter_def = self.core.filters[name].PARAMS
            
            cleaned_params = {}
            for k, v in params_dict.items():
                cleaned_params[k] = v
                if v != filter_def[k]["default"]:
                    is_active = True
            
            if is_active:
                filter_list.append((name, cleaned_params))
                
        return filter_list

    def on_slider_released(self, name):
        """Handle slider release: save state to history without 'baking' into base."""
        # Check if actually changed
        if self.slider_values == self.slider_state_before_move:
            return

        desc = f"Adjust {name}"
        
        # Save the PREVIOUS state so Undo restores it.
        # The current state is already reflected in the UI and 'current_image'.
        # History stack represents "Ways to go back".
        self.core.push_history(self.slider_state_before_move, description=desc)
        
        try:
            # We need to trigger the main window to update size estimation etc.
            # But apply_combined_filters already updated the image.
            # Maybe just signal?
            self.filter_applied.emit()
        except Exception:
            pass

    def on_slider_changed(self, filter_name, param_key, value):
        self.slider_values[filter_name][param_key] = value
        self.apply_combined_filters()

    def apply_combined_filters(self):
        """Apply all active sliders to the current base image."""
        if self.core.original_image is None:
            return

        self.core.in_preview = True
        
        filter_list = self.get_active_filters()
        
        if not filter_list:
            if self.core.original_image:
                self.core.current_image = self.core.original_image.copy()
        else:
            self.core.apply_preview_filters(filter_list)
        
        self.filter_applied.emit()

    def set_slider_state(self, state):
        """Update slider positions from a dictionary without triggering new calculations."""
        # Use deepcopy to ensure we don't hold references to history items
        self.slider_values = copy.deepcopy(state)
        
        # Update widgets
        for name, params_dict in self.slider_widgets.items():
            if name in state:
                for k, slider in params_dict.items():
                    if k in state[name]:
                        val = state[name][k]
                        slider.blockSignals(True)
                        slider.setValue(val)
                        slider.blockSignals(False)
            else:
                # If filter not in state (e.g. state from before new filter added), reset to default?
                # or just ignore. Safety: reset to default if missing.
                # Actually, if we just set values from state, we should probably reset others.
                # But typically state is full snapshot.
                pass
        
        # update display based on restored state
        self.apply_combined_filters()
