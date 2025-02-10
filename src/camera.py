import numpy as np
import util
import glm

class Camera:
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.znear = 0.01
        self.zfar = 100
        self.fovy = np.pi / 2
        self.position = np.array([0.0, 0.0, 3.0]).astype(np.float32)
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

    def get_view_matrix(self):
        return np.array(glm.lookAt(self.position, self.target, self.up))
    
    def get_project_matrix(self):
        project_mat = glm.perspective(
            self.fovy,
            self.w/self.h,
            self.znear,
            self.zfar
        )
        return np.array(project_mat).astype(np.float32)
    
    def get_htanfovxy_focal(self):
        htany = np.tan(self.fovy / 2)
        htanx = htany / self.h * self.w
        focal = self.w / (2 * htanx)
        return [htanx, htany, focal]