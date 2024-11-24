import cv2
from PIL import Image, ImageTk
import numpy as np
from camera_transform import CameraTransformer


class GUIDraw:
    def __init__(self, root, camera_manager, gui_setup):
        self.root = root
        self.camera_manager = camera_manager
        self.gui_setup = gui_setup
        self.running = True
        self.transformer = CameraTransformer()
        self.check_overexposure = False
        self.overexposure_threshold = 225
        self.update_frames()

    def enable_overexposure_check(self, threshold):
        self.check_overexposure = True
        self.overexposure_threshold = threshold

    def disable_overexposure_check(self):
        self.check_overexposure = False

    def update_overexposure_threshold(self, threshold):
        self.overexposure_threshold = threshold

    def draw_center_x_circle(self, frame):
        center_x = frame.shape[1] // 2
        center_y = frame.shape[0] // 2
        length = 90
        radius = 150

        cv2.line(frame, (center_x - length, center_y - length), (center_x + length, center_y + length), (0, 255, 0), 15)
        cv2.line(frame, (center_x - length, center_y + length), (center_x + length, center_y - length), (0, 255, 0), 15)
        cv2.circle(frame, (center_x, center_y), radius, (0, 255, 0), 15)

        return frame

    def update_frames(self):
        for i in range(self.gui_setup.grid_rows):
            for j in range(self.gui_setup.grid_cols):
                idx = i * self.gui_setup.grid_cols + j
                if idx < len(self.camera_manager.cameras):
                    if self.camera_manager.camera_status[idx]:
                        if self.camera_manager.cameras[idx].isOpened():
                            ret, frame = self.camera_manager.cameras[idx].read()
                            if ret:
                                # Rotate and convert to grayscale
                                frame = self.transformer.rotate_frame(frame)
                                gray_frame = self.transformer.to_grayscale(frame)
                                gray_frame_bgr = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)
                                
                                # Optional: Check for overexposure
                                if self.check_overexposure:
                                    gray_frame_bgr = self.transformer.highlight_overexposed_pixels(
                                        gray_frame_bgr, self.overexposure_threshold
                                    )

                                # Draw X and circle
                                final_frame = self.draw_center_x_circle(gray_frame_bgr)
                                self.display_frame(i, j, final_frame)
                        else:
                            self.display_camera_message(i, j, f"Please connect camera {idx}")
                    else:
                        self.display_camera_message(i, j, f"Please connect camera {idx}")
                else:
                    self.display_camera_message(i, j, f"Please connect camera {idx}")
        if self.running:
            self.root.after(10, self.update_frames)

    def display_frame(self, row, col, frame):
        """Display the frame in the corresponding label if it exists."""
        if self.gui_setup.labels[row][col] is not None:  # Check if label exists
            aspect_ratio = frame.shape[1] / frame.shape[0]
            new_width = self.gui_setup.preview_width
            new_height = int(new_width / aspect_ratio)
            if new_height > self.gui_setup.preview_height:
                new_height = self.gui_setup.preview_height
                new_width = int(new_height * aspect_ratio)
            frame = cv2.resize(frame, (new_width, new_height))

            black_image = np.zeros((self.gui_setup.preview_height, self.gui_setup.preview_width, 3), dtype=np.uint8)
            x_offset = (self.gui_setup.preview_width - new_width) // 2
            y_offset = (self.gui_setup.preview_height - new_height) // 2
            black_image[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = frame

            cv2image = cv2.cvtColor(black_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.gui_setup.labels[row][col].imgtk = imgtk
            self.gui_setup.labels[row][col].configure(image=imgtk)

    def display_camera_message(self, row, col, message):
        """Display a message in the corresponding label if it exists."""
        if self.gui_setup.labels[row][col] is not None:  # Check if label exists
            black_image = np.zeros((self.gui_setup.preview_height, self.gui_setup.preview_width, 3), dtype=np.uint8)
            cv2.putText(black_image, message, (10, self.gui_setup.preview_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            img = Image.fromarray(black_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.gui_setup.labels[row][col].imgtk = imgtk
            self.gui_setup.labels[row][col].configure(image=imgtk)

    def on_closing(self):
        self.running = False
        for cap in self.camera_manager.cameras:
            if cap is not None and cap.isOpened():
                cap.release()
        self.root.destroy()
