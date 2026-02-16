from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QPushButton,
    QSizePolicy,
    QGroupBox
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

        # Separate filters into Parametric (Sliders) and Simple (Buttons)
        simple_filters = []

        for name in sorted(self.core.filters.keys()):
            filter_obj = self.core.filters[name]
            if not getattr(filter_obj, "HAS_PARAMS", False):
                simple_filters.append(name)

        # --- Simple Filters (Buttons) ---
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
        """Apply a destructive filter to the base image."""
        
        # Capture current slider state from sibling ColorsTab to ensure it persists in history
        slider_state = {}
        if self.parent() and hasattr(self.parent(), "colors_tab"):
            slider_state = self.parent().colors_tab.slider_values

        def _on_finished(ok):
            # We need to refresh the preview.
            # But we also need to re-apply any active sliders from the Colors tab!
            # The MainWindow or Sidebar should handle this coordination.
            self.filter_applied.emit()
            
        self.window().run_background_task(
            self.core.apply_filter,
            args=[name],
            kwargs={"slider_state": slider_state},
            on_finished=_on_finished,
            msg=f"Applying {name}..."
        )
