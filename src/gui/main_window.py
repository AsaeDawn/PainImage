from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QToolBar, QStatusBar
from PySide6.QtCore import Qt, QThread, Signal
from editor.editor_core import EditorCore

from gui.topbar import TopBar
from gui.image_view import ImageView
from gui.sidebar import SideBar
from gui.styles import DARK_STYLE, LIGHT_STYLE

class UpscaleWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, upscaler, image):
        super().__init__()
        self.upscaler = upscaler
        self.image = image

    def run(self):
        try:
            result = self.upscaler.upscale(self.image)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PainImage - Modern Editor")
        self.resize(1200, 760)

        # Core backend
        self.core = EditorCore()

        self.upscaler = self.core.ai_features["Upscaler"]

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

        # self.upscale_manager = UpscaleModelManager()
        # self.upscaler_engine = UpscalerEngine(self.upscale_manager.model_path)


        # # Add topbar as toolbar area
        # self.addToolBar(self.topbar)  # QToolBar-like, but works with QWidget since PySide6 supports it

        

        toolbar = QToolBar("TopBar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.addWidget(self.topbar)
        self.addToolBar(toolbar)

        self.setStatusBar(QStatusBar())

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
            self.sidebar.filters_tab.reset_all_sliders()
            self.refresh_preview()

    def on_redo(self):
        if self.core.redo():
            self.sidebar.filters_tab.reset_all_sliders()
            self.refresh_preview()

    def on_toggle_theme(self):
        self._dark = not self._dark
        self.apply_theme()

    def refresh_preview(self):
        if self._showing_original:
            if self.core.initial_image:
                self.image_view.display_image(self.core.initial_image)
            return

        if self.core.current_image:
            self.image_view.display_image(self.core.current_image)
        else:
            self.image_view.clear()

    def run_upscale_from_ai(self):
        if not self.core.current_image:
            self.statusBar().showMessage("No image loaded", 3000)
            return

        self.statusBar().showMessage("AI Upscaling in progress... please wait.")
        self.topbar.setEnabled(False)
        self.sidebar.setEnabled(False)

        self.worker = UpscaleWorker(self.upscaler, self.core.current_image)
        self.worker.finished.connect(self._on_upscale_finished)
        self.worker.error.connect(self._on_upscale_error)
        self.worker.start()

    def _on_upscale_finished(self, result):
        self.core.push_history()
        self.core.original_image = result.copy()
        self.core.current_image = result.copy()
        self.refresh_preview()
        
        self.topbar.setEnabled(True)
        self.sidebar.setEnabled(True)
        self.statusBar().showMessage("Upscaling complete!", 3000)

    def _on_upscale_error(self, message):
        self.topbar.setEnabled(True)
        self.sidebar.setEnabled(True)
        self.statusBar().showMessage(f"Upscaling error: {message}", 5000)


