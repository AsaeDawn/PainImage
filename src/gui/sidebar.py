from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from gui.tabs.filters_tab import FiltersTab
from gui.tabs.tools_tab import ToolsTab
from gui.tabs.ai_tab import AITab

class SideBar(QWidget):
    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8,8,8,8)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)

        self.filters_tab = FiltersTab(self.core, parent=self)
        self.tools_tab = ToolsTab(self.core, parent=self)
        self.ai_tab = AITab(self.core, parent=self)

        self.tabs.addTab(self.filters_tab, "Filters")
        self.tabs.addTab(self.tools_tab, "Tools")
        self.tabs.addTab(self.ai_tab, "AI")

        layout.addWidget(self.tabs)
