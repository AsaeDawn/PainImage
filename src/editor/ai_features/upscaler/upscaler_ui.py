from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, Signal

class UpscalerUI(QWidget):
    upscale_clicked = Signal()

    def __init__(self, model_manager):
        super().__init__()

        self.manager = model_manager

        self.layout = QVBoxLayout(self)

        self.status_label = QLabel("Upscale x4 using RealESRGAN-Lite")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.download_btn = QPushButton("Download Model (7 MB)")
        self.upscale_btn = QPushButton("Upscale Image")
        self.progress = QProgressBar()
        self.progress.setVisible(False)

        self.layout.addWidget(self.download_btn)
        self.layout.addWidget(self.upscale_btn)
        self.layout.addWidget(self.progress)

        # Hide download if model already exists
        if self.manager.model_exists():
            self.download_btn.hide()

        self.download_btn.clicked.connect(self.download_model)
        self.upscale_btn.clicked.connect(self.upscale_clicked.emit)

    def download_model(self):
        self.progress.setVisible(True)

        def update_progress(p):
            self.progress.setValue(p)

        self.manager.download_model(update_progress)
        self.download_btn.hide()
        self.status_label.setText("Model installed ✔")
