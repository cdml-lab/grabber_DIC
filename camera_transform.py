import cv2

class CameraTransformer:
    @staticmethod
    def rotate_frame(frame, rotate=False):
        if rotate:
            return cv2.rotate(frame, cv2.ROTATE_180)
        return frame


    @staticmethod
    def to_grayscale(frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def highlight_overexposed_pixels(frame, threshold):
        red_channel = frame[:, :, 2]
        gray_frame = cv2.cvtColor(red_channel, cv2.COLOR_GRAY2BGR)
        overexposed_mask = red_channel > threshold
        gray_frame[overexposed_mask] = [0, 0, 255]
        return gray_frame
