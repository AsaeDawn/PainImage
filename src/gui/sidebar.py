import customtkinter as ctk
from tkinter import filedialog


from gui.popups.resize_popup import open_resize_popup
from gui.popups.compress_popup import open_compress_popup
from gui.popups.convert_popup import open_convert_popup

class Sidebar(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, width=200, corner_radius=0)

        self.master = master

        # == File Buttons ==
        ctk.CTkButton(self, text="Open Image", command=self.open_image).pack(pady=10, padx=20)
        ctk.CTkButton(self, text="Save Image", command=self.save_image).pack(pady=10, padx=20)

        # == Filters ==
        ctk.CTkLabel(self, text="Filters:", anchor="w").pack(pady=15, padx=20)

        for filter_name in self.master.core.filters:
            ctk.CTkButton(
                self,
                text=filter_name,
                command=lambda name=filter_name: self.apply_filter(name)
            ).pack(pady=5, padx=20)

        # == Tools ==
        ctk.CTkLabel(self, text="Tools:", anchor="w").pack(pady=15, padx=20)

        ctk.CTkButton(self, text="Resize Image", 
                      command=lambda: open_resize_popup(self.master)).pack(pady=5, padx=20)

        ctk.CTkButton(self, text="Compress Image",
                      command=lambda: open_compress_popup(self.master)).pack(pady=5, padx=20)

        ctk.CTkButton(self, text="Convert Format",
                      command=lambda: open_convert_popup(self.master)).pack(pady=5, padx=20)


    # ------------------------------------------------------
    # IMAGE LOAD/SAVE
    # ------------------------------------------------------
    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.gif")]
        )
        if path:
            self.master.core.load_image(path)
            self.master.refresh_preview()

    def save_image(self):
        if not self.master.core.current_image:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("WebP", "*.webp")]
        )
        if path:
            self.master.core.current_image.save(path)

    # ------------------------------------------------------
    # APPLY FILTER
    # ------------------------------------------------------
    def apply_filter(self, name):
        self.master.core.apply_filter(name)
        self.master.refresh_preview()