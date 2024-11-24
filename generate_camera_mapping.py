import re
import subprocess
import numpy as np

class CameraMappingGenerator:
    def __init__(self, num_cameras):
        self.num_cameras = num_cameras

    def generate_mapping(self):
        """Extract, sort, and save the device-specific IDs in a NumPy matrix."""
        try:
            device_list = self.get_usb_cameras()
            device_ids = [(i, self.extract_unique_id(device)) for i, device in enumerate(device_list)]

            # Sort the device IDs based on the identifier (second element in tuple)
            sorted_device_ids = sorted(device_ids, key=lambda x: x[1])

            # Create a NumPy matrix with old_index, new_index, and device-specific ID
            mapping_matrix = np.array([[old_idx, new_idx, device_id] 
                                       for new_idx, (old_idx, device_id) in enumerate(sorted_device_ids)])

            # Save the matrix to a NumPy file
            np.save('camera_mapping.npy', mapping_matrix)
            print("camera_mapping.npy generated successfully.")
        except Exception as e:
            print(f"Error generating camera mapping: {e}")

    def get_usb_cameras(self):
        """Retrieve the list of USB cameras using a system command."""
        try:
            # Use a system command to list connected USB devices, filter for camera-related descriptions
            result = subprocess.run(['wmic', 'path', 'Win32_PnPEntity', 'where', "Description like '%USB%'"], 
                                    capture_output=True, text=True)
            device_list = result.stdout.splitlines()

            # Filter for devices that are likely to be cameras (e.g., by name or class)
            usb_cameras = [device for device in device_list if 'Camera' in device or 'usbvideo' in device.lower()]

            return usb_cameras
        except Exception as e:
            print(f"Error retrieving USB devices: {e}")
            return []

    def extract_unique_id(self, device_string):
        """Extract the device-specific ID from the USB string."""
        try:
            # Universal regex to extract the portion after the last '&'
            match = re.search(r'\\(?:[^\\]+&)+([A-Z0-9]+)&0&\d{4}', device_string)
            if match:
                return match.group(1)  # Return the extracted unique part
            else:
                print(f"Could not extract ID from: {device_string}")
        except Exception as e:
            print(f"Error extracting ID: {e}")
        return None


if __name__ == "__main__":
    # Set the number of cameras based on your system
    num_cameras = 12  # Adjust based on your actual setup

    # Generate the camera mapping
    generator = CameraMappingGenerator(num_cameras)
    generator.generate_mapping()
