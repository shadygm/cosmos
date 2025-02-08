import numpy as np
import util
class Camera:
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.fovy = np.pi / 2
        self.position = np.array([0.0, 0.0, 0.0]).astype(np.float32)
        self.target = np.array([0.0, 0.0, 0.0]).astype(np.float32)
        self.up = np.array([0.0, -1.0, 0.0]).astype(np.float32)
        self.yaw = -np.pi / 2
        self. pitch = 0

        self.dirty_pose = True
        self.dirty_intrinsic = True

        self.last_x = 640
        self.last_y = 360

        self.first_mouse = True

        self.is_leftmouse_pressed = False
        self.is_rightmouse_pressed = False

        self.log = util.get_logger()

    def process_translation(self, dx, dy):

        self.log.info(f"dx: {dx}, dy: {dy}")

        front = self.target - self.position
        if np.linalg.norm(front) <= 0:
            front = np.array([0.0, 0.0, 1.0])

        front = front / np.linalg.norm(front)

        right = np.cross(front, self.up)

        move_direction = front * dy + right * dx

        norm = np.linalg.norm(move_direction)
        if norm > 0:
            move_direction = move_direction / norm

        self.position += move_direction 
        self.target += move_direction 

        self.dirty_pose = True

        