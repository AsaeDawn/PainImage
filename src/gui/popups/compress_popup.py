import customtkinter as ctk

def open_compress_popup(app):

    win = ctk.CTkToplevel(app)
    win.title("Compress Image")
    win.geometry("300x150")

    entry = ctk.CTkEntry(win, placeholder_text="Target Size (KB)")
    entry.pack(pady=10)

    def apply():
        kb = int(entry.get())
        app.core.current_image = app.core.tools["Compress to Size"](app.core.current_image, kb)
        app.refresh_preview()
        win.destroy()

    ctk.CTkButton(win, text="Apply", command=apply).pack(pady=10)
