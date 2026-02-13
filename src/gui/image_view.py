from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QLabel, QGraphicsItem
from PySide6.QtCore import Qt, Signal, QTimer, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent
from PIL import Image
from utils.image_utils import pil_image_to_qpixmap

class ImageView(QGraphicsView):
    request_open = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup Scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Image Item
        self._item = QGraphicsPixmapItem()
        self._item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.scene.addItem(self._item)
        
        # State
        self._current_pil = None
        self._zoom_factor = 1.15
        self._fit_to_window = True  # Initially fit to window
        self._empty = True
        
        # Setup View
        self.setRenderHint(QPainter.Antialiasing, False) # Pixel exact rendering usually better for editors, strictly
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setFrameShape(QGraphicsView.Shape.NoFrame) # No border

        # Placeholder (Overlay Widget)
        self.placeholder = QLabel("Click or drag an image here to open", self)
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) # Let clicks pass through if needed, but we handle click manually
        # Actually, if we want click-to-open logic on the placeholder, we can handle it in mousePress of View
        self.placeholder.show()

        # Drag & Drop
        self.setAcceptDrops(True)
        
        # Styling to match previous look (roughly)
        self.setStyleSheet("background: transparent;") # Let parent style handle bg? or set specific

    def display_image(self, pil_img):
        """Display the image. Handles high-DPI scaling and proxy previews."""
        self._current_pil = pil_img
        self._empty = False
        self.placeholder.hide()
        
        # Convert to Pixmap
        pix = pil_image_to_qpixmap(pil_img)
        self._item.setPixmap(pix)
        
        # Handle Proxy Scaling (if in preview mode)
        # We need to know if this is a proxy to scale it up visually
        scale = 1.0
        if hasattr(self.parent(), "core"):
            core = self.parent().core
            if core.in_preview and core.original_image:
                # Calculate scale factor relative to original
                orig_w, _ = core.original_image.size
                if pil_img.width > 0:
                    scale = orig_w / pil_img.width
        
        # Apply scale to item so it matches "Scene Logic Coordinates" (Full Res)
        self._item.setScale(scale)
        
        # Update Scene Rect to match the logical size of the image
        scene_w = pix.width() * scale
        scene_h = pix.height() * scale
        self.scene.setSceneRect(0, 0, scene_w, scene_h)

        # If we are in "Fit to Window" mode, or this is the first load
        if self._fit_to_window:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def clear(self):
        self._current_pil = None
        self._empty = True
        self._item.setPixmap(QPixmap())
        self.placeholder.show()
        self._fit_to_window = True
        self.resetTransform()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep centered placeholder
        self.placeholder.resize(self.width(), self.height())
        
        if self._fit_to_window and not self._empty:
             self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        if self._empty:
            return

        # Zoom Logic
        self._fit_to_window = False # User manually zoomed
        
        adj = self._zoom_factor
        if event.angleDelta().y() < 0:
            adj = 1.0 / self._zoom_factor
        
        self.scale(adj, adj)

    def mousePressEvent(self, event: QMouseEvent):
        # Click to open if empty
        if self._empty and event.button() == Qt.LeftButton:
             self.request_open.emit("")
             return
             
        super().mousePressEvent(event)

    # Drag & Drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.request_open.emit(path)
