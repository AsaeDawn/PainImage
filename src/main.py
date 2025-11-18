import customtkinter as ctk 
def main():
    # initializing app window
    ctk.set_appearance_mode("dark") # options: system / light / dark

    app = ctk.CTk()
    app.title("Pain Image")
    app.geometry("800x600")

    # Label to confirm window works
    label = ctk.CTkLabel(app, text="Welcome to Pain Image Editor!  :D",font=("Arial", 24))
    label.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    main()
