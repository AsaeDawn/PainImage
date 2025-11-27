from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from editor.editor_core import EditorCore

from gui.topbar import TopBar
from gui.image_view import ImageView
from gui.sidebar import SideBar
from gui.styles import DARK_STYLE, LIGHT_STYLE
from PySide6.QtWidgets import QToolBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PainImage - Modern Editor")
        self.resize(1200, 760)

        # Core backend
        self.core = EditorCore()

        self._showing_original = False


        # Top bar
        self.topbar = TopBar(self)
        self.topbar.open_image.connect(self.on_open)
        self.topbar.save_image.connect(self.on_save)
        self.topbar.toggle_preview_original.connect(self.on_toggle_preview)
        self.topbar.undo_requested.connect(self.on_undo)
        self.topbar.redo_requested.connect(self.on_redo)
        self.topbar.toggle_theme.connect(self.on_toggle_theme)

        # Central layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Image view (left)
        self.image_view = ImageView(self)
        self.image_view.request_open.connect(self._open_path)

        # Sidebar (right)
        self.sidebar = SideBar(self.core, parent=self)
        # When a filter is applied inside FiltersTab → refresh preview
        self.sidebar.filters_tab.filter_applied.connect(self.refresh_preview)


        layout.addWidget(self.image_view, 3)
        layout.addWidget(self.sidebar, 1)

        # # Add topbar as toolbar area
        # self.addToolBar(self.topbar)  # QToolBar-like, but works with QWidget since PySide6 supports it

        

        toolbar = QToolBar("TopBar")
        toolbar.setMovable(False)  # keep slim & fixed
        toolbar.setFloatable(False)
        toolbar.addWidget(self.topbar)
        self.addToolBar(toolbar)


        # default theme
        self._dark = True
        self.apply_theme()

    def apply_theme(self):
        if self._dark:
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

    # ---------- Actions ----------
    def on_open(self):
        # open dialog from image_view
        self.image_view.mousePressEvent  # keep for API but call file dialog via image_view click behavior
        # We use a small helper: open a file using QFileDialog
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)")
        if path:
            self._open_path(path)

    def _open_path(self, path):
        # Use core to load image
        self.core.load_image(path)
        # refresh preview
        self.refresh_preview()
        self._showing_original = False


    def on_save(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg);;WebP (*.webp)")
        if not path:
            return
        # if current_image is a PIL Image, save directly
        if self.core.current_image:
            self.core.current_image.save(path)

    def on_toggle_preview(self):
        self._showing_original = not self._showing_original
        self.refresh_preview()

    def on_undo(self):
        if self.core.undo():
            self.refresh_preview()

    def on_redo(self):
        if self.core.redo():
            self.refresh_preview()

    def on_toggle_theme(self):
        self._dark = not self._dark
        self.apply_theme()

    def refresh_preview(self):
        if self._showing_original:
            if self.core.original_image:
                self.image_view.display_image(self.core.original_image)
            return

        if self.core.current_image:
            self.image_view.display_image(self.core.current_image)
        else:
            self.image_view.clear()

