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
        vbox = QVBoxLayout(container)
        vbox.setSpacing(10)

        for name in sorted(self.core.filters.keys()):
            filter_obj = self.core.filters[name]

            # ---------- PARAMETER (DELTA) FILTER ----------
            if getattr(filter_obj, "HAS_PARAMS", False):
                label = QLabel(name)
                label.setStyleSheet("font-weight: bold;")
                vbox.addWidget(label)

                # expect DELTA param
                param = filter_obj.PARAMS["delta"]

                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(param["min"])
                slider.setMaximum(param["max"])
                slider.setValue(0)  # ALWAYS neutral
                slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                # preview lifecycle
                slider.sliderPressed.connect(self.core.begin_preview)

                slider.valueChanged.connect(
                    lambda value, n=name: self.preview_delta_filter(n, value)
                )

                slider.sliderReleased.connect(
                    lambda s=slider: self.commit_delta_preview(s)
                )

                vbox.addWidget(slider)

            # ---------- SIMPLE FILTER ----------
            else:
                btn = QPushButton(name)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                btn.clicked.connect(
                    lambda checked=False, n=name: self.apply_simple_filter(n)
                )
                vbox.addWidget(btn)

        vbox.addStretch(1)
        scroll.setWidget(container)
        layout.addWidget(scroll)

    # -------------------------
    # Filter handlers
    # -------------------------
    def apply_simple_filter(self, name):
        self.core.apply_filter(name)
        self.filter_applied.emit()

    def preview_delta_filter(self, name, delta):
        self.core.apply_preview_filter(name, delta=delta)
        self.filter_applied.emit()

    def commit_delta_preview(self, slider):
        self.core.commit_preview()
        slider.setValue(0)  # reset to neutral every time
        self.filter_applied.emit()
