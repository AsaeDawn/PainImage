from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class AITab(QWidget):
    def __init__(self, core, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("AI tools will appear here later."))
        layout.addStretch(1)
