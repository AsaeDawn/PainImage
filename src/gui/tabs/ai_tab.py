from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar
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
        # Model Download Section
        # ------------------------
        self.btn_download = QPushButton("Download Upscale Model (7 MB)")
        self.progress = QProgressBar()
        self.progress.setVisible(False)

        layout.addWidget(self.btn_download)
        layout.addWidget(self.progress)

        # Hide download button if model exists
        if self.upscaler.manager.exists():
            self.btn_download.hide()

        self.btn_download.clicked.connect(self.download_model)

        # ------------------------
        # Upscale Button
        # ------------------------
        self.btn_upscale = QPushButton("Upscale Image (x4)")
        layout.addWidget(self.btn_upscale)
        self.btn_upscale.clicked.connect(self.upscale_requested.emit)

        layout.addStretch(1)

    # ------------------------------------
    # Download model (RealESRGAN Lite)
    # --------------------------------------------------
    # Download the NCNN model files (bin + param)
    # --------------------------------------------------
    def download_model(self):
        # We use a signal-based progress update
        self.progress.setVisible(True)
        self.btn_download.setEnabled(False)

        def _on_finished(ok):
            self.progress.hide()
            self.btn_download.hide()
            if ok:
                self.window().statusBar().showMessage("AI Models downloaded successfully!", 5000)
            else:
                self.btn_download.setEnabled(True)
                self.window().statusBar().showMessage("Failed to download AI Models.", 5000)

        # We run the manager.download in the background
        self.window().run_background_task(
            self.upscaler.manager.download,
            kwargs={"progress_callback": self.progress.setValue},
            on_finished=_on_finished,
            msg="Downloading AI Models (this may take a minute)..."
        )
    # --------------------------------------------------
    # Upscaling is handled by MainWindow
    # --------------------------------------------------
    def trigger_upscale(self):
        self.upscale_requested.emit()
