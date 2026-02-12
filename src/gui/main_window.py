from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QToolBar, QStatusBar, QMessageBox
from PySide6.QtCore import Qt, QThread, Signal
from editor.editor_core import EditorCore

from gui.topbar import TopBar
from gui.image_view import ImageView
from gui.sidebar import SideBar
from gui.history_panel import HistoryPanel
from gui.styles import DARK_STYLE, LIGHT_STYLE

class TaskWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

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

        self.upscaler = self.core.ai_features.get("Upscaler")

        self._showing_original = False


        # Top bar
        self.topbar = TopBar(self)
        self.topbar.open_image.connect(self.on_open)
        self.topbar.save_image.connect(self.on_save)
        self.topbar.toggle_preview_original.connect(self.on_toggle_preview)
        self.topbar.undo_requested.connect(self.on_undo)
        self.topbar.redo_requested.connect(self.on_redo)
        self.topbar.redo_requested.connect(self.on_redo)
        self.topbar.toggle_history.connect(self.on_toggle_history)
        self.topbar.toggle_theme.connect(self.on_toggle_theme)

        # Central layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Image view (left)
        self.image_view = ImageView(self)
        self.image_view.request_open.connect(self._on_image_view_request_open)

        # Sidebar (right)
        self.sidebar = SideBar(self.core, parent=self)
        # When a filter is applied inside FiltersTab → refresh preview
        self.sidebar.filters_tab.filter_applied.connect(self.refresh_preview)


        # History Panel (Left, hidden by default)
        self.history_panel = HistoryPanel(self)
        self.history_panel.hide()

        layout.addWidget(self.history_panel, 0)
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
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)")
        if path:
            self._open_path(path)

    def _on_image_view_request_open(self, path):
        if not path:
            self.on_open()
        else:
            self._open_path(path)

    def _open_path(self, path):
        # Use core to load image
        self.core.load_image(path)
        # refresh preview
        self.refresh_preview()
        self._showing_original = False


    def on_save(self):
        from PySide6.QtWidgets import QFileDialog
        import os
        path, selected_filter = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg);;WebP (*.webp)")
        if not path:
            return
        if self.core.current_image:
            # Determine format from file extension, fall back to PNG
            ext = os.path.splitext(path)[1].lower()
            fmt_map = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}
            fmt = fmt_map.get(ext, "PNG")
            # Append extension if missing
            if not ext:
                if "JPEG" in selected_filter:
                    fmt = "JPEG"
                    path += ".jpg"
                elif "WebP" in selected_filter:
                    fmt = "WEBP"
                    path += ".webp"
                else:
                    fmt = "PNG"
                    path += ".png"
            if fmt == "JPEG":
                self.core.current_image.save(path, format=fmt, quality=90)
            else:
                self.core.current_image.save(path, format=fmt)

    def on_toggle_preview(self):
        self._showing_original = not self._showing_original
        self.refresh_preview()

    def on_undo(self):
        def _on_undo_finished(slider_state):
            if slider_state is not None:
                self.sidebar.filters_tab.set_slider_state(slider_state)
                self.refresh_preview()

        self.run_background_task(
            self.core.undo,
            kwargs={"current_slider_state": self.sidebar.filters_tab.slider_values},
            on_finished=_on_undo_finished,
            msg="Undoing..."
        )

    def on_redo(self):
        def _on_redo_finished(slider_state):
            if slider_state is not None:
                self.sidebar.filters_tab.set_slider_state(slider_state)
                self.refresh_preview()

        self.run_background_task(
            self.core.redo,
            kwargs={"current_slider_state": self.sidebar.filters_tab.slider_values},
            on_finished=_on_redo_finished,
            msg="Redoing..."
        )

    def on_toggle_history(self):
        if self.history_panel.isVisible():
            self.history_panel.hide()
            self.topbar.history_btn.setChecked(False)
        else:
            self.history_panel.show()
            self.topbar.history_btn.setChecked(True)
            self.update_history_panel()

    def update_history_panel(self):
        self.history_panel.update_history(self.core.action_log, self.core.action_index)

    def on_toggle_theme(self):
        self._dark = not self._dark
        self.apply_theme()

    def refresh_preview(self, estimate_size=False):
        if self._showing_original:
            if self.core.initial_image:
                self.image_view.display_image(self.core.initial_image)
            return

        image = self.core.current_image
        if image:
            self.image_view.display_image(image)
            info = self.core.get_image_info(estimate_size=estimate_size)
            if info:
                msg = f"Resolution: {info['width']}x{info['height']}  |  Approx. Size ({info['format']}): {info['size_kb']} KB"
                self.statusBar().showMessage(msg)
        else:
            self.image_view.clear()
            self.statusBar().clearMessage()
        
        # Always update history panel if visible
        if self.history_panel.isVisible():
            self.update_history_panel()

    def run_upscale_from_ai(self):
        if not self.core.current_image:
            self.statusBar().showMessage("No image loaded", 3000)
            return

        self.statusBar().showMessage("AI Upscaling in progress... please wait.")
        self.sidebar.ai_tab.start_progress()
        self.topbar.setEnabled(False)

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
        self.sidebar.ai_tab.stop_progress("Done! Upscaled successfully.")
        self.statusBar().showMessage("Upscaling complete!", 3000)

    def _on_upscale_error(self, message):
        self.topbar.setEnabled(True)
        self.sidebar.ai_tab.show_error("Upscaling failed.")
        self.statusBar().showMessage("Upscaling failed.", 5000)
        
        # Show a detailed message box for AI errors
        QMessageBox.critical(self, "AI Error", f"The AI upscaler encountered an error:\n\n{message}")

    # ---------- Background Tasks ----------
    def run_background_task(self, func, on_finished=None, args=None, kwargs=None, msg="Processing..."):
        """Run a core function in a background thread."""
        self.statusBar().showMessage(msg)
        self.topbar.setEnabled(False)
        self.sidebar.setEnabled(False)

        args = args or []
        kwargs = kwargs or {}
        
        self.task_worker = TaskWorker(func, *args, **kwargs)
        
        def _finished(result):
            self.topbar.setEnabled(True)
            self.sidebar.setEnabled(True)
            if on_finished:
                on_finished(result)
            else:
                self.refresh_preview()
            self.statusBar().showMessage("Done!", 3000)

        def _error(err):
            self.topbar.setEnabled(True)
            self.sidebar.setEnabled(True)
            self.statusBar().showMessage(f"Error: {err}", 5000)

        self.task_worker.finished.connect(_finished)
        self.task_worker.error.connect(_error)
        self.task_worker.start()


