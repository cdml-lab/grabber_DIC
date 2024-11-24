import os
import cv2
import csv
from tkinter import filedialog, messagebox
import tkinter as tk
from datetime import datetime

class FileSaver:
    def __init__(self, root, camera_manager, gui_setup):
        self.root = root
        self.camera_manager = camera_manager
        self.gui_setup = gui_setup  # Now directly passing the GUISetup object
        self.specimen_directory = None
        self.num_cameras = self.camera_manager.num_cameras
        
        # Ensure the serial port or any resources are properly closed when the app is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        # Perform any cleanup actions here before closing
        for i in range(self.num_cameras):
            if self.camera_manager.cameras[i] is not None:
                self.camera_manager.cameras[i].release()  # Release the camera if it's open

        print("Closing the application and releasing resources.")
        self.root.quit()  # Close the Tkinter window
        self.root.destroy()  # Destroy the window completely

    def choose_specimen(self):
        # Ask if it's a new or existing specimen every time capture is pressed
        is_new_specimen = messagebox.askyesno("Specimen", "Is this a new specimen?")
        if is_new_specimen:
            # New specimen: create folders
            self.specimen_directory = filedialog.askdirectory(title="Select Directory for New Specimen")
            if self.specimen_directory:
                self.create_folders_for_new_specimen()
        else:
            # Existing specimen: check existing folders
            self.specimen_directory = filedialog.askdirectory(title="Select Directory of Existing Specimen")
            if self.specimen_directory:
                self.check_existing_specimen_folders()

    def create_folders_for_new_specimen(self):
        # Create folders named 101, 102, ..., based on the number of cameras
        for i in range(self.num_cameras):
            folder_name = os.path.join(self.specimen_directory, f"{101 + i}")
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
        messagebox.showinfo("Folders Created", f"Created {self.num_cameras} folders for the new specimen.")
        
        # Create the 'Results' folder
        results_folder = os.path.join(self.specimen_directory, 'Results')
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
            print(f"Created Results folder at {results_folder}")
        
        # Create an empty 'environmental_data.csv' file inside the Results folder
        csv_file_path = os.path.join(results_folder, 'environmental_data.csv')
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            # Writing header for the CSV file
            writer.writerow(['Serial Number', 'Date', 'Time', 'Temperature (°C)', 'Relative Humidity (%)', 'Wind Speed (m/s)'])
        print(f"Created environmental_data.csv inside Results folder")

    def check_existing_specimen_folders(self):
        # Check if the number of folders matches the number of cameras
        expected_folders = [str(101 + i) for i in range(self.num_cameras)]
        existing_folders = [name for name in os.listdir(self.specimen_directory) if os.path.isdir(os.path.join(self.specimen_directory, name))]

        missing_folders = set(expected_folders) - set(existing_folders)
        if missing_folders:
            messagebox.showwarning("Missing Folders", f"The following folders are missing: {', '.join(missing_folders)}")

    def save_images(self):
        if not self.specimen_directory:
            messagebox.showwarning("Error", "No specimen directory selected.")
            return

        # Save images in the appropriate folders
        for i in range(self.camera_manager.num_cameras):
            if self.camera_manager.camera_status[i]:
                if self.camera_manager.cameras[i].isOpened():
                    ret, frame = self.camera_manager.cameras[i].read()
                    if ret:
                        # save the red channel as a TIFF file
                        
                        red_channel = frame[:, :, 2]

                        # Determine the next index for saving
                        folder_name = os.path.join(self.specimen_directory, f"{101 + i}")
                        existing_files = sorted([f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, f))])
                        next_index = len(existing_files) + 1

                        filename = f"{folder_name}/{101 + i}_{next_index}.tiff"
                        cv2.imwrite(filename, red_channel)
                        print(f"Saved {filename}")

    def capture(self):
        # Ask whether it is a new or existing specimen every time capture is pressed
        self.choose_specimen()

        # Now save images after processing the specimen type
        if self.specimen_directory:
            self.save_images()

            # Also, save the environmental data into the CSV file
            self.read_arduino_data()

    def read_arduino_data(self):
        # Ensure that specimen directory and environmental data CSV file exist
        results_folder = os.path.join(self.specimen_directory, 'Results')
        csv_file_path = os.path.join(results_folder, 'environmental_data.csv')

        # Get the current date and time
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # Get environmental data from GUI setup (directly from the GUISetup object passed during initialization)
        temperature = self.gui_setup.temperature
        humidity = self.gui_setup.humidity
        wind_speed = self.gui_setup.wind_speed

        # Write the data into the CSV file
        with open(csv_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            serial_number = len(open(csv_file_path).readlines())  # Count lines to get the serial number
            writer.writerow([serial_number, date_str, time_str, temperature, humidity, wind_speed])

        print(f"Environmental data recorded: {date_str}, {time_str}, Temp: {temperature}, Humidity: {humidity}, Wind Speed: {wind_speed}")
