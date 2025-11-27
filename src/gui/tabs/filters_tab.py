from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton, QWidget, QSizePolicy
from PySide6.QtCore import Signal


class FiltersTab(QWidget):
    filter_applied = Signal() 
    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6,6,6,6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(8)

        # create a button for each filter
        for name in sorted(self.core.filters.keys()):
            btn = QPushButton(name)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(self.make_apply(name))
            vbox.addWidget(btn)

        vbox.addStretch(1)
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def make_apply(self, name):
        def _apply():
            # push history from core (editor_core.apply_filter already pushes history if you implemented it)
            # If not, you can call self.core.push_history() here before apply.
            self.core.apply_filter(name)
            # notify parent window via signal or direct call (we assume parent MainWindow will read core)
            # if self.parent():
            #     try:
            #         self.parent().parent().refresh_preview()
            #     except Exception:
            #         pass
            self.filter_applied.emit() 
            
        return _apply
