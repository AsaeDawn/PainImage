from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt

class HistoryPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("historyPanel")
        self.setFixedWidth(240)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Title
        title_lbl = QLabel("History")
        title_lbl.setObjectName("historyTitle")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("historyList")
        self.list_widget.setSelectionMode(QListWidget.NoSelection) # We handle highlighing programmatically
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.list_widget)
        
    def update_history(self, action_log, action_index):
        """
        Rebuild the history list.
        action_log: list of strings (descriptions)
        action_index: int, index of the current state (0-based)
        """
        self.list_widget.clear()
        
        for i, desc in enumerate(action_log):
            # Format text based on state
            if i < action_index:
                # Past actions
                text = f"  {desc}"
                item = QListWidgetItem(text)
                # Style handled by QListWidget usually, but we can set flags if needed
            elif i == action_index:
                # Current state
                text = f"▸ {desc}"
                item = QListWidgetItem(text)
                item.setSelected(True) # Use selection for "current" styling
                # Force strictly current style if needed via custom role or just rely on selection style
            else:
                # Future (undone) actions
                text = f"  {desc}"
                item = QListWidgetItem(text)
                # We'll style these as 'disabled' or 'future' in CSS
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled) # Disable interaction/visuals
                
            self.list_widget.addItem(item)
            
        # Scroll to current
        if action_index >= 0 and action_index < self.list_widget.count():
            self.list_widget.scrollToItem(self.list_widget.item(action_index))
