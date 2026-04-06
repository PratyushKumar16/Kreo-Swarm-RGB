import bundle_fix # Must be first to set environment variables for bundled app
import customtkinter as ctk
from swarmkreo.controller import KreoController
import tkinter as tk
from tkinter import colorchooser

class KreoGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fix for macOS menu crash in bundled apps
        try:
            self.create_macos_menu()
        except:
            pass

        self.controller = KreoController()

        self.title("Kreo Swarm RGB Controller v1.0.3")
        self.geometry("600x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.selected_color = "#FF0000"
        self.r, self.g, self.b = 255, 0, 0

        self.setup_ui()
        self.check_device()

    def check_device(self):
        # Initial check to see if device is connected
        try:
            dev = self.controller.find_device()
            if dev:
                name = dev.get('product_string', 'Kreo Keyboard')
                self.status_label.configure(text=f"Connected: {name}", text_color="#2ecc71")
            else:
                self.status_label.configure(text="Device not found. Connect via USB/Dongle.", text_color="#e67e22")
        except Exception as e:
            self.status_label.configure(text=f"Check failed: {str(e)}", text_color="#e74c3c")

    def create_macos_menu(self):
        # Create a dummy menu to satisfy macOS requirements in bundled apps
        menubar = tk.Menu(self)
        try:
            app_menu = tk.Menu(menubar, name='apple')
            menubar.add_cascade(menu=app_menu)
        except:
            pass
        self.config(menu=menubar)

    def setup_ui(self):
        # Title
        self.label = ctk.CTkLabel(self, text="Kreo Swarm Backlight", font=ctk.CTkFont(size=28, weight="bold"))
        self.label.pack(pady=(30, 20))

        # Color Preview
        self.color_preview = ctk.CTkFrame(self, width=120, height=120, corner_radius=15, fg_color=self.selected_color)
        self.color_preview.pack(pady=10)

        # Color Button
        self.color_button = ctk.CTkButton(self, text="Pick Color", command=self.pick_color, 
                                           width=220, height=50, font=ctk.CTkFont(size=16))
        self.color_button.pack(pady=15)

        # Mode Selection
        self.mode_label = ctk.CTkLabel(self, text="Lighting Mode:", font=ctk.CTkFont(size=14))
        self.mode_label.pack(pady=(15, 5))
        
        self.mode_var = ctk.StringVar(value="Static")
        self.mode_menu = ctk.CTkOptionMenu(self, values=["Static", "Breathing", "Wave", "Reactive", "Off"], 
                                           variable=self.mode_var, width=220, height=45, font=ctk.CTkFont(size=15))
        self.mode_menu.pack(pady=5)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=15)

        # Apply Button
        self.apply_button = ctk.CTkButton(self, text="Apply Settings", command=self.apply_settings, 
                                           fg_color="#2ecc71", hover_color="#27ae60",
                                           width=280, height=65, font=ctk.CTkFont(size=18, weight="bold"))
        self.apply_button.pack(pady=25)

    def pick_color(self):
        color = colorchooser.askcolor(title="Choose color")[1]
        if color:
            self.selected_color = color
            self.color_preview.configure(fg_color=color)
            # Convert hex to RGB
            h = color.lstrip('#')
            self.r, self.g, self.b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def get_mode_hex(self, mode_name):
        modes = {
            "Static": "01",
            "Breathing": "02",
            "Wave": "03",
            "Reactive": "04",
            "Off": "00" # Pure guess for 'Off' based on common patterns
        }
        return modes.get(mode_name, "01")

    def apply_settings(self):
        mode_hex = self.get_mode_hex(self.mode_var.get())
        self.status_label.configure(text="Applying...", text_color="yellow")
        self.update()

        try:
            print(f"Applying settings: RGB({self.r}, {self.g}, {self.b}), Mode: {mode_hex}")
            success = self.controller.apply_settings(self.r, self.g, self.b, mode_hex)
            if success:
                print("Settings applied successfully!")
                self.status_label.configure(text="Applied Successfully!", text_color="#2ecc71")
            else:
                self.status_label.configure(text="Error: Connection failed", text_color="#e74c3c")
        except Exception as e:
            print(f"Exception during apply: {str(e)}")
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#e74c3c")

if __name__ == "__main__":
    app = KreoGUI()
    app.mainloop()
