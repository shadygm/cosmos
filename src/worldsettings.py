from camera import Camera
# from gaussian_renderer import GaussianRenderer
from gaussian_representation import GaussianSet
class WorldSettings():
    def __init__(self):

        self.world_camera = Camera(720, 1280)
        self.world_settings = None
        self.window = None
        self.glfw_renderer = None
        self.input_handler = None
        self.imgui_manager = None
        # self.gauss_renderer = GaussianRenderer()
        self.gaussian_set = None

        # Parameters
        self.time_scale = 1000.0

    def process_translation(self, dx, dy):
        dx *= self.time_scale
        dy *= self.time_scale
        self.world_camera.process_translation(dx, dy)

    def get_num_gaussians(self):
        return len(self.gaussian_set) if self.gaussian_set is not None else 0
    
    def load_ply(self, file_path):
        self.gaussian_set = GaussianSet.from_ply(file_path)
        # self.gauss_renderer.update_gaussian_data(self.gaussian_set)
        # self.gauss_renderer.sort_and_update()
        # self.gauss_renderer.update_camera_intrin()
        # self.gauss_renderer.update_camera_pose()