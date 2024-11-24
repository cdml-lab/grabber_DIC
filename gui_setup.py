import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from file_saving import FileSaver  # Assuming file_saving.py exists
import serial
import threading

class GUISetup:
    def __init__(self, root, camera_manager):
        self.root = root
        self.num_cameras = camera_manager.num_cameras  # Set the number of cameras from the camera manager
        self.grid_rows = 3
        self.grid_cols = 4
        self.preview_width = 240
        self.preview_height = 180

        # Use the camera_mapping to get the new indices
        self.camera_mapping = camera_manager.camera_mapping

        # Initialize labels to hold camera previews
        self.labels = [[None for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]

        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                idx = i * self.grid_cols + j
                if idx < len(self.camera_mapping):  # Ensure the index is within the range of cameras
                    old_index, new_index, _ = self.camera_mapping[idx]  # Get the new index from the mapping
                    self.labels[i][j] = tk.Label(self.root, text=f"Camera {new_index}", width=self.preview_width, height=self.preview_height)
                    self.labels[i][j].grid(row=i, column=j, padx=5, pady=5)

        # Initialize FileSaver with gui_setup
        self.file_saver = FileSaver(root, camera_manager, self)

        # Additional setup for the GUI (buttons, preview windows, etc.)
        self.setup_buttons()
        self.setup_preview()

        # Set up the labels for temperature, humidity, and wind speed (bold text)
        self.temp_label = tk.Label(self.root, text="Temperature: -- °C", font=("Arial", 12, "bold"))
        self.humidity_label = tk.Label(self.root, text="Humidity: -- %", font=("Arial", 12, "bold"))
        self.wind_speed_label = tk.Label(self.root, text="Wind Speed: -- m/s", font=("Arial", 12, "bold"))

        # Position these labels next to the capture button
        self.temp_label.grid(row=self.grid_rows, column=1, padx=10, pady=10, sticky="w")
        self.humidity_label.grid(row=self.grid_rows, column=2, padx=10, pady=10, sticky="w")
        self.wind_speed_label.grid(row=self.grid_rows, column=3, padx=10, pady=10, sticky="w")

        # Initialize serial communication with Arduino
        self.serial_port = serial.Serial('COM5', 9600, timeout=1)

        # Variables to hold sensor data
        self.temperature = "--"
        self.humidity = "--"
        self.wind_speed = "--"

        # Start the thread to read data from the Arduino
        threading.Thread(target=self.read_arduino_data, daemon=True).start()

        # Start updating the GUI with sensor data
        self.update_gui()

    def setup_buttons(self):
        """Set up buttons for the GUI."""
        # Example button setup
        self.capture_button = ttk.Button(self.root, text="Capture", command=self.capture_images)
        self.capture_button.grid(row=self.grid_rows, column=0, columnspan=1, pady=10)

    def setup_preview(self):
        """Set up the preview labels or windows."""
        # Example preview setup
        self.preview_text = ScrolledText(self.root, width=60, height=10)
        self.preview_text.grid(row=self.grid_rows + 1, column=0, columnspan=self.grid_cols, pady=10)

    def capture_images(self):
        """Capture images from the cameras."""
        self.file_saver.capture()

    def read_arduino_data(self):
        """ Continuously reads data from the Arduino in a separate thread """
        while True:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    data = line.split(',')
                    self.temperature = data[0].split(': ')[1].strip() 
                    self.humidity = data[1].split(': ')[1].strip() 
                    self.wind_speed = data[2].split(': ')[1].strip() 
            except Exception as e:
                print(f"Error reading from Arduino: {e}")

    def update_gui(self):
        """ Updates the GUI with the latest sensor data every 100 ms """
        # Update the labels with the latest sensor data
        self.temp_label.config(text=f"Temperature: {self.temperature}")
        self.humidity_label.config(text=f"Humidity: {self.humidity}")
        self.wind_speed_label.config(text=f"Wind Speed: {self.wind_speed}")

        # Schedule the next GUI update in 100 ms
        self.root.after(100, self.update_gui)
