import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

from image_ops import apply_grayscale, rotate_left, rotate_right

class ImageEditorApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("PainImage - Image Editor")
        self.geometry("600x400")
        self.minsize(600, 300)

        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.pack(side="left", fill="y")

        # Sidebar title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="TOOLS",
            font=("Arial", 18, "bold")
        )
        self.sidebar_title.pack(pady=(20, 10))

        # Buttons
        self.open_btn = ctk.CTkButton(
            self.sidebar,
            text="Open Image",
            command=self.open_image,
            height=45
        )
        self.open_btn.pack(pady=10, padx=20, fill="x")

        self.save_btn = ctk.CTkButton(
            self.sidebar,
            text="Save Image",
            command=self.save_image,
            state="disabled",
            height=45
        )
        self.save_btn.pack(pady=10, padx=20, fill="x")

        # Gray Filter
        self.gray_btn = ctk.CTkButton(
            self.sidebar, text="Grayscale Filter", command=self.apply_gray, state="disabled"
        )
        self.gray_btn.pack(pady=10, padx=20)

        # Rotate Filters
        self.rotate_left_btn = ctk.CTkButton(
            self.sidebar, text="Rotate Left", command=self.rotate_left_action, state="disabled"
        )
        self.rotate_left_btn.pack(pady=10, padx=20)
        
        self.rotate_right_btn = ctk.CTkButton(
            self.sidebar, text="Rotate Right", command=self.rotate_right_action, state="disabled"
        )
        self.rotate_right_btn.pack(pady=10, padx=20)

        # Main display area
        self.display_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#111111", border_width=1, border_color="#333")
        self.display_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Image display label
        self.image_label = ctk.CTkLabel(
            self.display_frame,
            text="Drop or Open an Image",
            anchor="center",
            font=("Arial", 20, "italic")
        )
        self.image_label.pack(expand=True, padx=20, pady=20)

        self.loaded_image = None
        self.display_image = None

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.gif")]
        )
        if not file_path:
            return

        self.loaded_image = Image.open(file_path)
        self.show_image(self.loaded_image)
        self.save_btn.configure(state="normal")
        self.gray_btn.configure(state="normal")
        self.rotate_left_btn.configure(state="normal")
        self.rotate_right_btn.configure(state="normal")
        


    def save_image(self):
        if self.loaded_image is None:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("WebP", "*.webp")
            ]
        )
        if save_path:
            self.loaded_image.save(save_path)

    def show_image(self, img):
        frame_w = self.display_frame.winfo_width()
        frame_h = self.display_frame.winfo_height()

        if frame_w < 50 or frame_h < 50:
            frame_w, frame_h = 800, 600

        img_preview = img.copy()
        img_preview.thumbnail((frame_w, frame_h))

        self.display_image = ImageTk.PhotoImage(img_preview)
        self.image_label.configure(image=self.display_image, text="")

    def apply_gray(self):
        if self.loaded_image is None:
            return
        
        # Process image
        self.loaded_image = apply_grayscale(self.loaded_image)
        
        # Update preview
        self.show_image(self.loaded_image)
    
    def rotate_left_action(self):
        if self.loaded_image is None:
            return

        # Process image
        self.loaded_image = rotate_left(self.loaded_image)

        #update preview
        self.show_image(self.loaded_image)
    
    def rotate_right_action(self):
        if self.loaded_image is None:
            return

        # Process image
        self.loaded_image = rotate_right(self.loaded_image)

        #update preview
        self.show_image(self.loaded_image)
