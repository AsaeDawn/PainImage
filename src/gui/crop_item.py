from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPen, QColor, QBrush, QPainter, QCursor

class CropItem(QGraphicsObject):
    """
    A QGraphicsItem that provides a resizable cropping rectangle.
    Displays handles and dims the area outside the crop.
    """
    crop_changed = Signal() 

    def __init__(self, rect, parent=None):
        super().__init__(parent)
        self._image_rect = rect # The full image area (limit)
        self._crop_rect = rect  # The current crop area
        self._ratio = None      # Aspect ratio (width / height)
        
        # State
        self._drag_handle = None 
        self._start_pos = None # Scene pos
        self._start_crop_rect = None
        
        # Appearance
        self._mask_color = QColor(0, 0, 0, 160)
        self._border_pen = QPen(Qt.white, 1, Qt.DashLine)
        self._handle_size = 10
        self._handle_brush = QBrush(Qt.white)
        self._handle_pen = QPen(Qt.black, 1)

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setZValue(100) 

    def set_image_rect(self, rect):
        self._image_rect = rect
        self._crop_rect = rect
        self.prepareGeometryChange()
        self.update()

    def set_ratio(self, ratio):
        self._ratio = ratio
        if self._ratio:
             self._enforce_ratio()
        self.update()

    def get_crop_rect(self):
        return self._crop_rect

    def boundingRect(self):
        return self._image_rect

    def paint(self, painter, option, widget):
        # 1. Dim mask (Subtraction)
        painter.setBrush(self._mask_color)
        painter.setPen(Qt.NoPen)
        
        outer = self._image_rect
        inner = self._crop_rect.intersected(outer)

        # Draw 4 rects to form the "hole"
        # Top
        if inner.top() > outer.top():
            painter.drawRect(QRectF(outer.left(), outer.top(), outer.width(), inner.top() - outer.top()))
        # Bottom
        if inner.bottom() < outer.bottom():
             painter.drawRect(QRectF(outer.left(), inner.bottom(), outer.width(), outer.bottom() - inner.bottom()))
        # Left (between top and bottom of inner)
        if inner.left() > outer.left():
             painter.drawRect(QRectF(outer.left(), inner.top(), inner.left() - outer.left(), inner.height()))
        # Right (between top and bottom of inner)
        if inner.right() < outer.right():
             painter.drawRect(QRectF(inner.right(), inner.top(), outer.right() - inner.right(), inner.height()))

        # 2. Border
        painter.setPen(self._border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(inner)

        # 3. Handles
        self._draw_handles(painter, inner)

    def _draw_handles(self, painter, rect):
        painter.setPen(self._handle_pen)
        painter.setBrush(self._handle_brush)
        hs = self._handle_size
        hs2 = hs / 2.0

        coords = [
            rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight(), # Corners
            QPointF(rect.center().x(), rect.top()),    # Top Mid
            QPointF(rect.center().x(), rect.bottom()), # Bottom Mid
            QPointF(rect.left(), rect.center().y()),   # Left Mid
            QPointF(rect.right(), rect.center().y())   # Right Mid
        ]
        
        for p in coords:
            painter.drawRect(QRectF(p.x() - hs2, p.y() - hs2, hs, hs))

        # Center crosshair or something? Optional.

    def _hit_test(self, pos):
        """Returns handle ID or None."""
        rect = self._crop_rect
        hs = self._handle_size + 5 # Hit tolerance
        
        # Check corners (priority)
        if (pos - rect.topLeft()).manhattanLength() < hs: return 'tl'
        if (pos - rect.topRight()).manhattanLength() < hs: return 'tr'
        if (pos - rect.bottomRight()).manhattanLength() < hs: return 'br'
        if (pos - rect.bottomLeft()).manhattanLength() < hs: return 'bl'
        
        # Check edges
        # We need to check distance to edge segments
        # Simple proximity check
        touch_l = abs(pos.x() - rect.left()) < hs and rect.top() < pos.y() < rect.bottom()
        touch_r = abs(pos.x() - rect.right()) < hs and rect.top() < pos.y() < rect.bottom()
        touch_t = abs(pos.y() - rect.top()) < hs and rect.left() < pos.x() < rect.right()
        touch_b = abs(pos.y() - rect.bottom()) < hs and rect.left() < pos.x() < rect.right()

        if touch_l: return 'l'
        if touch_r: return 'r'
        if touch_t: return 't'
        if touch_b: return 'b'

        if rect.contains(pos): return 'center'
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            handle = self._hit_test(event.pos())
            if handle:
                self._drag_handle = handle
                self._start_pos = event.pos() # Scene pos usually, but QGraphicsItem receives item pos
                self._start_crop_rect = self._crop_rect
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self._drag_handle:
            delta = event.pos() - self._start_pos
            self._resize_rect(delta)
            event.accept()
        else:
            handle = self._hit_test(event.pos())
            self._update_cursor(handle)

    def mouseReleaseEvent(self, event):
        self._drag_handle = None
        self._start_pos = None
        event.accept()

    def _update_cursor(self, handle):
        if not handle:
            self.setCursor(Qt.ArrowCursor)
            return
            
        mapping = {
            'tl': Qt.SizeFDiagCursor, 'br': Qt.SizeFDiagCursor,
            'tr': Qt.SizeBDiagCursor, 'bl': Qt.SizeBDiagCursor,
            't': Qt.SizeVerCursor, 'b': Qt.SizeVerCursor,
            'l': Qt.SizeHorCursor, 'r': Qt.SizeHorCursor,
            'center': Qt.SizeAllCursor
        }
        self.setCursor(mapping.get(handle, Qt.ArrowCursor))

    def _resize_rect(self, delta):
        if not self._start_crop_rect: return
        
        r = QRectF(self._start_crop_rect)
        limit = self._image_rect
        
        dx = delta.x()
        dy = delta.y()

        if self._drag_handle == 'center':
            r.translate(dx, dy)
            # Clamp
            if r.left() < limit.left(): r.moveLeft(limit.left())
            if r.top() < limit.top(): r.moveTop(limit.top())
            if r.right() > limit.right(): r.moveRight(limit.right())
            if r.bottom() > limit.bottom(): r.moveBottom(limit.bottom())
            
        else:
            # Edges/Corners
            # Logic: Update the side being dragged
            if 'l' in self._drag_handle: r.setLeft(min(r.left() + dx, r.right() - 10))
            if 'r' in self._drag_handle: r.setRight(max(r.right() + dx, r.left() + 10))
            if 't' in self._drag_handle: r.setTop(min(r.top() + dy, r.bottom() - 10))
            if 'b' in self._drag_handle: r.setBottom(max(r.bottom() + dy, r.top() + 10))
            
            # Simple clamping to image bounds
            r = r.intersected(limit)
            
            # Aspect Ratio Enforcement (Basic)
            if self._ratio:
                # This is complex to do perfectly with "intersected" clamping above
                # For now, let's re-expand or contract to match ratio based on width
                # or height priority.
                # A robust implementation is outside scope of this quick step, 
                # but we can do a simple check:
                pass # TODO: Add robust ratio constraint

        self._crop_rect = r
        self.prepareGeometryChange()
        self.update()

    def _enforce_ratio(self):
        # Center crop with ratio
        if not self._ratio: return
        
        r = self._crop_rect
        w = r.width()
        h = r.height()
        current_ratio = w / h if h > 0 else 1
        
        # Adjust dimensions to match target ratio, keeping center
        target_w = w
        target_h = w / self._ratio
        
        if target_h > self._image_rect.height():
             target_h = self._image_rect.height()
             target_w = target_h * self._ratio
             
        center = r.center()
        new_rect = QRectF(0, 0, target_w, target_h)
        new_rect.moveCenter(center)
        
        # Clamp if moved out
        new_rect = new_rect.intersected(self._image_rect)
        self._crop_rect = new_rect
        self.prepareGeometryChange()

