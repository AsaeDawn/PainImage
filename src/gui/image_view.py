from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFileDialog
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap
from PIL import Image
from utils.image_utils import pil_image_to_qpixmap

class ImageView(QWidget):
    request_open = Signal(str)  # optional: file path when clicking

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pix = None
        self._current_pil = None
        self._original_pil = None

        # Debounce timer for resizing
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._on_resize_timeout)

        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.placeholder = QLabel("Click or drag an image here to open")
        self.placeholder.setObjectName("placeholder")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.hide()

        layout.addWidget(self.placeholder)
        layout.addWidget(self.img_label, 1)

    def display_image(self, pil_img):
        """Set displayed image from PIL image, optimizing for speed during previews."""
        self._current_pil = pil_img
        
        w, h = pil_img.size
        label_w = self.img_label.width()
        label_h = self.img_label.height()
        
        # PERFORMANCE OPTIMIZATION: 
        # If we are in "preview" mode (moving sliders), we avoid the high-quality PIL resize
        # for every frame. Instead, we use a single QPixmap conversion and let Qt scale it fast.
        from editor.editor_core import EditorCore
        if hasattr(self.parent(), "core") and self.parent().core.in_preview:
            # Fast mode: convert original size once, scale in Qt
            pix = pil_image_to_qpixmap(pil_img)
            self.img_label.setPixmap(pix.scaled(
                label_w, label_h, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.FastTransformation
            ))
        elif label_w > 0 and label_h > 0:
            # High-quality mode: scale in PIL (for final display or idle state)
            scale = min(label_w / w, label_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            display_pil = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
            pix = pil_image_to_qpixmap(display_pil)
            self.img_label.setPixmap(pix)
        else:
            pix = pil_image_to_qpixmap(pil_img)
            self.img_label.setPixmap(pix)
        self.img_label.show()
        self.placeholder.hide()

    def clear(self):
        self._current_pil = None
        self._original_pil = None
        self.img_label.hide()
        self.placeholder.show()

    # resizing handling to rescale preview with debounce
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._current_pil:
            # During active resize, we stop any pending high-quality scale
            # and wait for the user to stop moving.
            self.resize_timer.start(150) # 150ms debounce

    def _on_resize_timeout(self):
        if self._current_pil:
            self.display_image(self._current_pil)

    # drag & drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.request_open.emit(path)

    # clicking to open - simplify to just emit signal
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Emit empty string to signal "user wants to open A file"
            # MainWindow will handle the dialog.
            self.request_open.emit("")
