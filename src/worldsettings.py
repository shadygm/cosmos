from camera import Camera
from gaussian_representation import GaussianData
import gaussian_representation
from gaussian_renderer import OpenGLRenderer
import util
import numpy as np

class WorldSettings():
    def __init__(self):

        self.world_camera = Camera(720, 1280)
        self.world_settings = None
        self.window = None
        self.input_handler = None
        self.imgui_manager = None
        self.gauss_renderer = None
        self.gaussian_set = gaussian_representation.naive_gaussian()

        # Parameters
        self.time_scale = 0.1
        self.model_transform_speed = 100.0
        self.scale_modifier = 1.0
        self.render_mode = 7
        self.auto_sort = False

        # Transformations
        self.model_transform = np.eye(4) 


    def process_model_translation(self, dx, dy):
        dx *= self.model_transform_speed
        dy *= self.model_transform_speed

        translation = np.eye(4, dtype=np.float32)
        translation[0, 3] = dx
        translation[1, 3] = dy

        self.model_transform = translation @ self.model_transform

        self.gauss_renderer.set_model_matrix(self.model_transform)

    def update_camera_pose(self):
        self.gauss_renderer.update_camera_pose()

    def update_render_mode(self, mode):
        self.render_mode = mode
        self.update_activated_render_state()

    def update_camera_intrin(self):
        self.gauss_renderer.update_camera_intrin()

    def create_gaussian_renderer(self):
        self.gauss_renderer = OpenGLRenderer(self.world_camera.w, self.world_camera.h, self)
        self.update_activated_render_state()

    def process_translation(self, dx, dy):
        dx *= self.time_scale
        dy *= self.time_scale
        self.world_camera.process_translation(dx, dy)

    def get_num_gaussians(self):
        return len(self.gaussian_set) if self.gaussian_set is not None else 0
    
    def load_ply(self, file_path):
        self.gaussian_set = gaussian_representation.from_ply(file_path)
        self.update_activated_render_state()

    def update_activated_render_state(self):
        self.gauss_renderer.update_gaussian_data(self.gaussian_set)
        self.gauss_renderer.sort_and_update()
        self.gauss_renderer.set_scale_modifier(self.scale_modifier)
        self.gauss_renderer.set_render_mode(self.render_mode - 4)
        self.gauss_renderer.set_model_matrix(self.model_transform)
        self.gauss_renderer.update_camera_pose()
        self.gauss_renderer.update_camera_intrin()
        self.gauss_renderer.set_render_resolution(self.world_camera.w, self.world_camera.h)