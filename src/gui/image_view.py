from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QLabel, QGraphicsItem
from PySide6.QtCore import Qt, Signal, QTimer, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent
from PIL import Image
from utils.image_utils import pil_image_to_qpixmap
from gui.crop_item import CropItem

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
        
        # Crop Item
        self.crop_item = None
        
        # State
        self._current_pil = None
        self._zoom_factor = 1.15
        self._fit_to_window = True  # Initially fit to window
        self._empty = True
        self._scale_factor = 1.0 # Current scale relative to full res
        
        # Setup View
        self.setRenderHint(QPainter.Antialiasing, False) 
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
        self.placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.placeholder.show()

        # Drag & Drop
        self.setAcceptDrops(True)
        
        self.setStyleSheet("background: transparent;")

    def display_image(self, pil_img):
        """Display the image. Handles high-DPI scaling and proxy previews."""
        self._current_pil = pil_img
        self._empty = False
        self.placeholder.hide()
        
        # Convert to Pixmap
        pix = pil_image_to_qpixmap(pil_img)
        self._item.setPixmap(pix)
        
        # Handle Proxy Scaling
        self._scale_factor = 1.0
        if hasattr(self.parent(), "core"):
            core = self.parent().core
            if core.in_preview and core.original_image:
                orig_w, _ = core.original_image.size
                if pil_img.width > 0:
                    self._scale_factor = orig_w / pil_img.width
        
        self._item.setScale(self._scale_factor)
        
        # Update Scene Rect
        scene_w = pix.width() * self._scale_factor
        scene_h = pix.height() * self._scale_factor
        self.scene.setSceneRect(0, 0, scene_w, scene_h)
        
        # Update Crop Item if active
        if self.crop_item:
            self.crop_item.set_image_rect(QRectF(0, 0, scene_w, scene_h))

        # If we are in "Fit to Window" mode, or this is the first load
        if self._fit_to_window:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def start_crop(self):
        """Enable crop mode."""
        if self._empty or self.crop_item: return
        
        # Create CropItem covering the whole image
        rect = self._item.boundingRect()
        # Scale logic: item bounding rect is in local coords (pixels). 
        # But we scaled the item.
        # We need the scene rect of the image.
        
        scene_rect = self.scene.sceneRect()
        self.crop_item = CropItem(scene_rect)
        self.scene.addItem(self.crop_item)
        
        # Disable panning while cropping? Or just let CropItem handle clicks?
        # CropItem handles clicks. BUT if user drags outside crop handles, View might Pan.
        # That's actually fine/good.
        self.setDragMode(QGraphicsView.NoDrag) # Disable hand drag to avoid confusion?
        # User might want to pan to see edges. 
        # But RightButton or MiddleButton usually pans in that case if Left is for Crop.
        # Let's disable HandDrag on Left Click by setting NoDrag, 
        # and maybe allow Panning via Middle Mouse or Space+Drag (standard).
        # For now, simplistic: Disable view panning to focus on Crop.
        
    def end_crop(self):
        """Disable crop mode."""
        if self.crop_item:
            self.scene.removeItem(self.crop_item)
            self.crop_item = None
            self.setDragMode(QGraphicsView.ScrollHandDrag) # Restore Pan

    def get_crop_box(self):
        """Return (left, top, right, bottom) tuple in ORIGINAL image coordinates."""
        if not self.crop_item: return None
        
        rect = self.crop_item.get_crop_rect()
        # rect is in scene coordinates (which matches Original Image dimensions because of our scaling logic)
        # So it should be 1:1 with Original Image properties.
        
        return (int(rect.left()), int(rect.top()), int(rect.right()), int(rect.bottom()))
        
    def set_crop_ratio(self, ratio):
        if self.crop_item:
            self.crop_item.set_ratio(ratio)

    def clear(self):
        self.end_crop()
        self._current_pil = None
        self._empty = True
        self._item.setPixmap(QPixmap())
        self.placeholder.show()
        self._fit_to_window = True
        self.resetTransform()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.placeholder.resize(self.width(), self.height())
        if self._fit_to_window and not self._empty:
             self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        if self._empty: return
        self._fit_to_window = False 
        adj = self._zoom_factor
        if event.angleDelta().y() < 0:
            adj = 1.0 / self._zoom_factor
        self.scale(adj, adj)

    def mousePressEvent(self, event: QMouseEvent):
        if self._empty and event.button() == Qt.LeftButton:
             self.request_open.emit("")
             return
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.request_open.emit(path)
