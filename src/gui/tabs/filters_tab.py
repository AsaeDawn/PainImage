from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QPushButton,
    QSizePolicy,
    QLabel,
    QSlider,
    QGroupBox,
    QFormLayout
)
from PySide6.QtCore import Signal, Qt


class FiltersTab(QWidget):
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

        # Separate filters into Parametric (Sliders) and Simple (Buttons)
        param_filters = []
        simple_filters = []

        for name in sorted(self.core.filters.keys()):
            filter_obj = self.core.filters[name]
            if getattr(filter_obj, "HAS_PARAMS", False):
                param_filters.append(name)
            else:
                simple_filters.append(name)

        # --- 1. Parametric Filters Grouped ---
        for name in param_filters:
            filter_obj = self.core.filters[name]
            params = getattr(filter_obj, "PARAMS", {})
            
            # Use QGroupBox for better visual separation
            group = QGroupBox(name)
            group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
            group_layout = QVBoxLayout(group)
            
            self.slider_values[name] = {}
            self.slider_widgets[name] = {}

            for param_key, param_info in params.items():
                # Default param setup
                min_val = param_info.get("min", 0)
                max_val = param_info.get("max", 100)
                default_val = param_info.get("default", 0)
                label_text = param_info.get("label", param_key.capitalize())

                # Initialize value
                self.slider_values[name][param_key] = default_val

                # UI Row
                row_layout = QVBoxLayout()
                lbl = QLabel(label_text)
                lbl.setStyleSheet("color: #555; font-size: 11px;")
                
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(min_val)
                slider.setMaximum(max_val)
                slider.setValue(default_val)
                slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
                # Connect signals
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

        # --- 2. Simple Filters (Buttons) ---
        if simple_filters:
            simple_group = QGroupBox("Quick Effects")
            simple_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
            simple_layout = QVBoxLayout(simple_group)
            
            for name in simple_filters:
                btn = QPushButton(name)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(
                    lambda checked=False, n=name: self.apply_simple_filter(n)
                )
                simple_layout.addWidget(btn)
            
            self.vbox.addWidget(simple_group)

        self.vbox.addStretch(1)
        scroll.setWidget(container)
        layout.addWidget(scroll)

    # -------------------------
    def apply_simple_filter(self, name):
        """Apply a destructive filter to the base image. Sliders are not touched."""
        def _on_finished(ok):
            # Re-apply slider preview on top of the new base
            self.apply_combined_filters()
            self.window().refresh_preview()

        self.window().run_background_task(
            self.core.apply_filter,
            args=[name],
            on_finished=_on_finished,
            msg=f"Applying {name}..."
        )

    def capture_before_move(self):
        """Store the current positions before a new adjustment starts."""
        # Deep copy needed for nested dictionaries
        import copy
        self.slider_state_before_move = copy.deepcopy(self.slider_values)

    def get_active_filters(self):
        """
        Build the list of active filters with their current slider values.
        Returns list of (filter_name, kwargs_dict)
        """
        filter_list = []
        for name, params_dict in self.slider_values.items():
            # Check if any param is different from default
            # We need to know default values to check "is active" efficiently.
            # Or just send everything. 
            # Optimization: check against default in core's filter params.
            
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
        # Create a description of what changed
        desc = f"Adjust {name}"
        
        self.core.push_history(self.slider_values, description=desc)
        
        try:
            self.window().refresh_preview(estimate_size=True)
        except Exception:
            pass

    def on_slider_changed(self, filter_name, param_key, value):
        self.slider_values[filter_name][param_key] = value
        self.apply_combined_filters()

    def apply_combined_filters(self):
        """Apply all active sliders to the current base image."""
        self.core.in_preview = True # Ensure preview mode is active
        
        filter_list = self.get_active_filters()
        
        # If no sliders are active, just show original base
        if not filter_list:
            if self.core.original_image:
                self.core.current_image = self.core.original_image.copy()
        else:
            self.core.apply_preview_filters(filter_list)
        
        self.filter_applied.emit()

    def reset_all_sliders(self):
        # iterate all filters and reset to default
        new_state = {}
        for name, params_dict in self.slider_values.items():
            new_state[name] = {}
            filter_def = self.core.filters[name].PARAMS
            for k in params_dict.keys():
                new_state[name][k] = filter_def[k]["default"]
                
        self.set_slider_state(new_state)

    def set_slider_state(self, state):
        """Update slider positions from a dictionary without triggering new calculations."""
        # State structure: { filter_name: { param: value } }
        import copy
        self.slider_values = copy.deepcopy(state)
        
        for name, params_dict in self.slider_widgets.items():
            if name in state:
                for k, slider in params_dict.items():
                    if k in state[name]:
                        val = state[name][k]
                        slider.blockSignals(True)
                        slider.setValue(val)
                        slider.blockSignals(False)
        
        # update display based on restored state
        self.apply_combined_filters()
