import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

from editor.editor_core import EditorCore 

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

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Sidebar: title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="TOOLS",
            font=("Arial", 18, "bold")
        )
        self.sidebar_title.pack(pady=(20, 10))

        # Sidebar: buttons
        self.open_btn = ctk.CTkButton(self.sidebar, text="Open Image", command=self.open_image)
        self.open_btn.pack(pady=10, padx=20)

        self.save_btn = ctk.CTkButton(self.sidebar, text="Save Image", command=self.save_image, state="disabled")
        self.save_btn.pack(pady=10, padx=20)

        # Dynamic Buttons Loader
        # Dynamic filter buttons
        ctk.CTkLabel(self.sidebar, text="Filters:", anchor="w").pack(pady=10, padx=20)

        for filter_name in self.core.filters:
            btn = ctk.CTkButton(
                self.sidebar,
                text=filter_name,
                command=lambda n=filter_name: self.apply_filter_action(n),
                state="disabled"
            )
            btn.pack(pady=5, padx=20)

            # store button so we can enable later
            if not hasattr(self, "filter_buttons"):
                self.filter_buttons = []
            self.filter_buttons.append(btn)


        # Placeholder: we'll add filter buttons dynamically later
        # So you never manually edit GUI code again

        # Right preview area
        self.display_frame = ctk.CTkFrame(self)
        self.display_frame.pack(side="right", fill="both", expand=True)

        self.image_label = ctk.CTkLabel(self.display_frame, text="No Image Loaded", anchor="center")
        self.image_label.pack(expand=True)

        self.display_image = None

        # -------------------------------
    # Image Loading & Saving
    # -------------------------------

    def open_image(self):
        for b in self.filter_buttons:
            b.configure(state="normal")

        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.gif")]
        )
        if not file_path:
            return

        self.core.load_image(file_path)
        self.show_image(self.core.current_image)
        self.save_btn.configure(state="normal")

    def save_image(self):
        if self.core.current_image is None:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("WebP", "*.webp")]
        )
        if save_path:
            self.core.current_image.save(save_path)

    # -------------------------------
    # Image Display
    # -------------------------------

    def show_image(self, img):
        frame_w = self.display_frame.winfo_width()
        frame_h = self.display_frame.winfo_height()

        if frame_w < 50 or frame_h < 50:
            frame_w, frame_h = 800, 600

        preview = img.copy()
        preview.thumbnail((frame_w, frame_h))

        self.display_image = ImageTk.PhotoImage(preview)
        self.image_label.configure(image=self.display_image, text="")

        # Main display area

        # Image display label

    def apply_filter_action(self, name):
        if self.core.apply_filter(name):
            self.show_image(self.core.current_image)

