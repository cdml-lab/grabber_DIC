import tkinter as tk
from camera_import import CameraManager
from generate_camera_mapping import CameraMappingGenerator
from gui_setup import GUISetup
from gui_draw import GUIDraw
from overexposure_check import OverexposureCheck

if __name__ == "__main__":
    root = tk.Tk()

    # Generate the camera mapping file
    num_cameras = 12  # Set this to the actual number of cameras in your setup
    mapping_generator = CameraMappingGenerator(num_cameras)
    mapping_generator.generate_mapping()

    # Initialize camera manager
    camera_manager = CameraManager(root)
    camera_manager.start()

    # Initialize GUI setup
    gui_setup = GUISetup(root, camera_manager)

    # Initialize GUI draw functionality
    gui_draw = GUIDraw(root, camera_manager, gui_setup)

    # Initialize OverexposureCheck with the gui_draw object
    overexposure_check = OverexposureCheck(root, gui_draw)

    # Assign the on_closing method to the window's close event
    root.protocol("WM_DELETE_WINDOW", gui_draw.on_closing)

    # Run the application
    root.mainloop()
