from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal


class AITab(QWidget):
    upscale_requested = Signal()    # tell MainWindow to upscale

    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core
        self.upscaler = self.core.ai_features.get("Upscaler")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6,6,6,6)

        title = QLabel("AI Tools")
        layout.addWidget(title)

        # ------------------------
        # Upscale Button
        # ------------------------
        self.btn_upscale = QPushButton("Upscale Image (x4)")
        layout.addWidget(self.btn_upscale)
        self.btn_upscale.clicked.connect(self.upscale_requested.emit)

        layout.addStretch(1)

    def trigger_upscale(self):
        self.upscale_requested.emit()

