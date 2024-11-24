import tkinter as tk
from tkinter import ttk

class OverexposureCheck:
    def __init__(self, root, gui_draw):
        self.root = root
        self.gui_draw = gui_draw
        self.threshold = tk.IntVar(value=225)  # Default threshold for overexposure
        self.active = tk.BooleanVar(value=False)  # Switch state

        # Frame for the overexposure controls
        self.frame = ttk.Frame(root)
        self.frame.grid(row=4, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

        # Switch to enable/disable overexposure checking
        self.switch = ttk.Checkbutton(
            self.frame,
            text="Check Overexposure",
            variable=self.active,
            command=self.toggle_overexposure
        )
        self.switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Slider to adjust the overexposure threshold
        self.slider = ttk.Scale(
            self.frame,
            from_=0,
            to=255,
            variable=self.threshold,
            orient=tk.HORIZONTAL,
            command=self.update_threshold,
            state="disabled"  # Initially disabled
        )
        self.slider.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def toggle_overexposure(self):
        if self.active.get():
            self.slider.configure(state="normal")  # Enable slider
            self.gui_draw.enable_overexposure_check(self.threshold.get())
        else:
            self.slider.configure(state="disabled")  # Disable slider
            self.gui_draw.disable_overexposure_check()

    def update_threshold(self, value):
        if self.active.get():
            try:
                threshold = int(float(value))  # Convert string to float, then to int
                self.gui_draw.update_overexposure_threshold(threshold)
            except ValueError:
                print(f"Invalid value received from slider: {value}")

    def on_closing(self):
        self.active.set(False)
        self.toggle_overexposure()
        self.frame.destroy()
