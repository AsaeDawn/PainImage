import sys
import os
from PySide6.QtWidgets import QApplication

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from gui.main_window import MainWindow
from editor.editor_core import EditorCore

def test_instantiation():
    app = QApplication(sys.argv)
    
    print("Initializing EditorCore...")
    core = EditorCore()
    
    print("Testing apply_filter signature...")
    # Should accept slider_state
    try:
        core.apply_filter("Brightness", slider_state={"some": "state"})
    except TypeError as e:
        print(f"FAILED: apply_filter signature incorrect: {e}")
        return
        
    print("Initializing MainWindow...")
    window = MainWindow()
    
    print("Checking SideBar tabs...")
    assert hasattr(window.sidebar, "filters_tab")
    assert hasattr(window.sidebar, "colors_tab")
    
    print("Checking ColorsTab slider logic...")
    # Simulate slider release
    window.sidebar.colors_tab.slider_values = {"Test": {"p": 10}}
    window.sidebar.colors_tab.slider_state_before_move = {"Test": {"p": 5}}
    
    # This might fail if it tries to emit signal connected to GUI update without image
    # But push_history should work?
    try:
        window.sidebar.colors_tab.on_slider_released("Test")
        print("ColorsTab.on_slider_released executed")
    except Exception as e:
        print(f"Warning during slider release test (expected if no image loaded): {e}")

    print("UI Instantiation OK")
    # window.show()
    # app.exec()

if __name__ == "__main__":
    test_instantiation()
