import customtkinter as ctk

FORMATS = ["PNG", "JPEG", "WEBP"]

def open_convert_popup(app):

    win = ctk.CTkToplevel(app)
    win.title("Convert Format")
    win.geometry("250x200")

    for fmt in FORMATS:
        ctk.CTkButton(
            win, 
            text=fmt,
            command=lambda f=fmt: apply(app, f, win)
        ).pack(pady=5)


def apply(app, fmt, win):
    app.core.current_image = app.core.tools["Convert Format"](app.core.current_image, fmt)
    app.refresh_preview()
    win.destroy()
