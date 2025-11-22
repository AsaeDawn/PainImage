import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

from editor.editor_core import EditorCore 
from gui.sidebar import Sidebar
from gui.imageview import ImageView

class ImageEditorApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Name and Size of Window
        self.title("PainImage - Image Editor")
        self.geometry("600x400")
        self.minsize(600,300)

        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.core = EditorCore()

        # Layout: Left sidebar, right image viewer
        self.sidebar = Sidebar(self)
        self.sidebar.pack(side="left", fill="y")

        self.image_view = ImageView(self)
        self.image_view.pack(side="right", fill="both", expand=True)
    
    # Wrapper: Update preview
    def refresh_preview(self):
        if self.core.current_image:
            self.image_view.display(self.core.current_image)

    
