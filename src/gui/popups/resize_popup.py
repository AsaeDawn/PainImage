import customtkinter as ctk

def open_resize_popup(app):

    win = ctk.CTkToplevel(app)
    win.title("Resize Image")
    win.geometry("300x200")

    w_entry = ctk.CTkEntry(win, placeholder_text="Width")
    w_entry.pack(pady=10)

    h_entry = ctk.CTkEntry(win, placeholder_text="Height")
    h_entry.pack(pady=10)

    def apply():
        width = int(w_entry.get())
        height = int(h_entry.get())
        
        app.core.push_history()
        
        app.core.current_image = app.core.tools["Resize Image"](app.core.current_image, width, height)
        app.refresh_preview()
        win.destroy()

    ctk.CTkButton(win, text="Apply", command=apply).pack(pady=10)
