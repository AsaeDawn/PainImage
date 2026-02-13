from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal

class TopBar(QWidget):
    open_image = Signal()
    save_image = Signal()
    toggle_preview_original = Signal()
    undo_requested = Signal()
    redo_requested = Signal()
    toggle_history = Signal()
    toggle_theme = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._original_preview_on = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Simple left-aligned area
        self.open_btn = QPushButton("Open")
        self.save_btn = QPushButton("Save")
        self.undo_btn = QPushButton("Undo")
        self.redo_btn = QPushButton("Redo")
        self.preview_btn = QPushButton("Preview Original")
        self.theme_btn = QPushButton("☀ Light")

        # Connect
        self.open_btn.clicked.connect(self.open_image.emit)
        self.save_btn.clicked.connect(self.save_image.emit)
        self.undo_btn.clicked.connect(self.undo_requested.emit)
        self.redo_btn.clicked.connect(self.redo_requested.emit)
        self.preview_btn.clicked.connect(self._on_preview_clicked)
        self.theme_btn.clicked.connect(self._on_theme_clicked)

        # Add to layout
        layout.addWidget(self.open_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.undo_btn)
        layout.addWidget(self.redo_btn)
        
        # History toggle
        self.history_btn = QPushButton("History")
        self.history_btn.setCheckable(True)
        self.history_btn.clicked.connect(self.toggle_history.emit)
        layout.addWidget(self.history_btn)

        layout.addStretch(1)
        layout.addWidget(self.preview_btn)
        layout.addWidget(self.theme_btn)

    def _on_preview_clicked(self):
        self._original_preview_on = not self._original_preview_on
        self.preview_btn.setText("Original: ON" if self._original_preview_on else "Preview Original")
        self.toggle_preview_original.emit()

    def _on_theme_clicked(self):
        self.theme_btn.setText("🌙 Dark" if "Light" in self.theme_btn.text() else "☀ Light")
        self.toggle_theme.emit()
