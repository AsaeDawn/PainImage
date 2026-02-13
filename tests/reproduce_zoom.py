
import sys
import os
from PySide6.QtWidgets import QApplication
from PIL import Image

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from gui.image_view import ImageView

def test_zoom():
    app = QApplication.instance() or QApplication(sys.argv)
    
    view = ImageView()
    
    # Create a dummy image (100x100 red)
    img = Image.new("RGB", (100, 100), "red")
    
    view.display_image(img)
    
    # Check initial state
    print(f"Initial matrix: {view.transform()}")
    
    # Simulate Zoom In (Wheel Event)
    # Transforming view manually to see if API works, 
    # but wheelEvent is hard to simulate without event loop active? 
    # We can just call wheelEvent handler if we mock the event, 
    # OR we can just check if scale() works.
    
    view.scale(1.5, 1.5)
    print(f"After Scale 1.5: {view.transform()}")
    
    if view.transform().m11() > 1.0:
        print("Zoom IN successful")
    else:
        print("Zoom IN failed")

    # Check Scene Rect
    rect = view.scene.sceneRect()
    print(f"Scene Rect: {rect}")
    if rect.width() == 100 and rect.height() == 100:
        print("Scene Rect Correct")
    else:
        print(f"Scene Rect Incorrect: {rect}")
        
    app.quit()

if __name__ == "__main__":
    test_zoom()
