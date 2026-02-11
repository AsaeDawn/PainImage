from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar
from PySide6.QtCore import Signal, QTimer


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

        # ------------------------
        # Progress / Status
        # ------------------------
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate (marquee) mode
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        layout.addStretch(1)

    # --- Progress control (called by MainWindow) ---

    def start_progress(self):
        """Show indeterminate progress bar and status text."""
        self.status_label.setText("Upscaling in progress...")
        self.status_label.setVisible(True)
        self.progress.setVisible(True)
        self.btn_upscale.setEnabled(False)

    def stop_progress(self, message="Done!"):
        """Hide progress bar and show a completion message."""
        self.progress.setVisible(False)
        self.status_label.setText(message)
        self.status_label.setVisible(True)
        self.btn_upscale.setEnabled(True)
        # Auto-hide the status after 4 seconds
        QTimer.singleShot(4000, lambda: self.status_label.setVisible(False))

    def show_error(self, message="Upscaling failed."):
        """Hide progress bar and show an error message."""
        self.progress.setVisible(False)
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #ff6b6b;")
        self.status_label.setVisible(True)
        self.btn_upscale.setEnabled(True)
        QTimer.singleShot(5000, self._reset_status_style)

    def _reset_status_style(self):
        self.status_label.setStyleSheet("")
        self.status_label.setVisible(False)

    def trigger_upscale(self):
        self.upscale_requested.emit()

