import customtkinter as ctk
from PIL import ImageTk

class ImageView(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.label = ctk.CTkLabel(self, text="No Image Loaded")
        self.label.pack(expand=True)
        self.display_image = None

    def display(self, img):
        preview = img.copy()
        preview.thumbnail((self.winfo_width(), self.winfo_height()))
        self.display_image = ImageTk.PhotoImage(preview)
        self.label.configure(image=self.display_image, text="")
