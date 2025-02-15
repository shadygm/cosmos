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

        # Sensitivity 
        self.rot_sensitivity = 0.02
        self.trans_sensitivity = 0.01
        self.zoom_sensitivity = 0.08
        self.roll_sensitivity = 0.03
        self.target_dist = 3.

    def process_translation(self, dx, dy):
        # Use the translation sensitivity factor instead of a huge division.
        front = self.target - self.position
        if np.linalg.norm(front) <= 0:
            front = np.array([0.0, 0.0, 1.0])
        front = front / np.linalg.norm(front)
        right = np.cross(front, self.up)

        # Calculate the move direction from keyboard input and scale it.
        move_direction = front * dy + right * dx
        norm = np.linalg.norm(move_direction)
        if norm > 0:
            move_direction = move_direction / norm

        # Apply the sensitivity factor here.
        self.position += move_direction * self.trans_sensitivity
        self.target   += move_direction * self.trans_sensitivity

        self.dirty_pose = True

    
    def process_scroll(self, xoffset, yoffset):
        front = self.target - self.position
        front = front / np.linalg.norm(front)
        self.position += front * yoffset * self.zoom_sensitivity
        self.target += front * yoffset * self.zoom_sensitivity
        self.dirty_pose = True

    def process_mouse(self, xpos, ypos):
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False
        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos
        self.last_x = xpos
        self.last_y = ypos

        if self.is_leftmouse_pressed:
            self.yaw += xoffset * self.rot_sensitivity
            self.pitch += yoffset * self.rot_sensitivity

            self.pitch = np.clip(self.pitch, -np.pi / 2, np.pi / 2)

            front = np.array([np.cos(self.yaw) * np.cos(self.pitch), 
                            np.sin(self.pitch), np.sin(self.yaw) * 
                            np.cos(self.pitch)])
            front = self._global_rot_mat() @ front.reshape(3, 1)
            front = front[:, 0]
            self.position[:] = - front * np.linalg.norm(self.position - self.target) + self.target
            
            self.dirty_pose = True
        
        if self.is_rightmouse_pressed:
            front = self.target - self.position
            front = front / np.linalg.norm(front)
            right = np.cross(self.up, front)
            self.position += right * xoffset * self.trans_sensitivity
            self.target += right * xoffset * self.trans_sensitivity
            cam_up = np.cross(right, front)
            self.position += cam_up * yoffset * self.trans_sensitivity
            self.target += cam_up * yoffset * self.trans_sensitivity
            
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
    
    def _global_rot_mat(self):
        x = np.array([1, 0, 0])
        z = np.cross(x, self.up)
        z = z / np.linalg.norm(z)
        x = np.cross(self.up, z)
        return np.stack([x, self.up, z], axis=-1)