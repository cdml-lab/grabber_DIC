import cv2
import threading
import numpy as np
from tkinter import messagebox

class CameraManager:
    def __init__(self, root):
        self.root = root
        self.num_cameras = 12  # Handle cameras from 0 to 11 (adjust if needed)
        self.cameras = [None] * self.num_cameras  # Initialize with None
        self.camera_status = [False] * self.num_cameras

        # Load the camera mapping from the NumPy matrix
        self.camera_mapping = self.load_camera_mapping()

    def start(self):
        threads = []
        # Use the new index to initialize the cameras according to the mapping
        for old_index, new_index, _ in self.camera_mapping:  # Unpack all three, ignore the third value (device-specific identifier)
            thread = threading.Thread(target=self.init_camera, args=(int(old_index), int(new_index)))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        successful_cameras = sum(self.camera_status)
        messagebox.showinfo("Cameras Imported", f"{successful_cameras} out of {self.num_cameras} cameras imported successfully. Press OK to proceed.")

    def init_camera(self, old_idx, new_idx):
        """Initialize the camera with the old index and store it at the new index."""
        try:
            cap = cv2.VideoCapture(old_idx)  # Open the camera using the original (old) index
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3264)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2448)
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'HEVC'))
                cap.set(cv2.CAP_PROP_FPS, 24)

                # Set the exposure time 
                exposure_time = -4  #   need to be adjust (range between -13 (darker) and -1 (brighter))
                cap.set(cv2.CAP_PROP_EXPOSURE, exposure_time)
                
                # Optionally, print or log the actual exposure time to verify
                actual_exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
                print(f"Camera {old_idx} exposure set to: {actual_exposure}")

                # Store the camera at the new index position
                self.camera_status[new_idx] = True
                self.cameras[new_idx] = cap
            else:
                print(f"Warning: Could not open camera {old_idx} (mapped to {new_idx}).")
                self.camera_status[new_idx] = False
                self.cameras[new_idx] = None
        except Exception as e:
            print(f"Error initializing camera {old_idx}: {e}")
            self.camera_status[new_idx] = False

    def load_camera_mapping(self):
        """Load camera mapping from the NumPy file and return it as a NumPy array."""
        try:
            camera_mapping = np.load('camera_mapping.npy')
            return camera_mapping
        except FileNotFoundError:
            print("camera_mapping.npy not found.")
            return np.empty((0, 3))  # Return an empty array if file not found
        except Exception as e:
            print(f"Error loading camera mapping: {e}")
            return np.empty((0, 3))
