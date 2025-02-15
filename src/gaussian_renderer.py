from OpenGL import GL as gl
import util
from camera import Camera
import gaussian_representation  # This module now provides the new Gaussian and GaussianSet classes.
import numpy as np

# Global buffers used for sorting
_sort_buffer_xyz = None
_sort_buffer_gausid = None  # used to tell whether gaussian set is reloaded

try:
    from OpenGL.raw.WGL.EXT.swap_control import wglSwapIntervalEXT
except:
    wglSwapIntervalEXT = None



def _sort_gaussian_cpu(gaussianset, view_mat):
    # Expect gaussianset to have a property 'xyz' (of shape (N,3))
    xyz = np.asarray(gaussianset.xyz)
    view_mat = np.asarray(view_mat)
    xyz_view = view_mat[None, :3, :3] @ xyz[..., None] + view_mat[None, :3, 3, None]
    depth = xyz_view[:, 2, 0]
    index = np.argsort(depth)
    index = index.astype(np.int32).reshape(-1, 1)
    return index

def _sort_gaussian_cupy(gaussianset, view_mat):
    import cupy as cp
    global _sort_buffer_gausid, _sort_buffer_xyz
    
    if gaussianset is None or len(gaussianset) == 0:
        util.get_logger().error("Gaussian data not loaded")
        return
    
    if _sort_buffer_gausid != id(gaussianset):
        _sort_buffer_xyz = cp.asarray(gaussianset.xyz)
        _sort_buffer_gausid = id(gaussianset)
    xyz = _sort_buffer_xyz
    view_mat = cp.asarray(view_mat)
    xyz_view = view_mat[None, :3, :3] @ xyz[..., None] + view_mat[None, :3, 3, None]
    depth = xyz_view[:, 2, 0]
    index = cp.argsort(depth)
    index = index.astype(cp.int32).reshape(-1, 1)
    index = cp.asnumpy(index)  # convert to numpy
    return index

def _sort_gaussian_torch(gaussianset, view_mat):
    import torch
    global _sort_buffer_gausid, _sort_buffer_xyz
    if _sort_buffer_gausid != id(gaussianset):
        _sort_buffer_xyz = torch.tensor(gaussianset.xyz).cuda()
        _sort_buffer_gausid = id(gaussianset)
    xyz = _sort_buffer_xyz
    xyz_view = view_mat[None, :3, :3] @ xyz[..., None] + view_mat[None, :3, 3, None]
    depth = xyz_view[:, 2, 0]
    index = torch.argsort(depth)
    index = index.type(torch.int32).reshape(-1, 1).cpu().numpy()
    return index

# Decide which sorting backend to use.
_sort_gaussian = None
try:
    import torch
    if not torch.cuda.is_available():
        raise ImportError
    util.logger.info("Detected torch cuda installed, will use torch as sorting backend")
    _sort_gaussian = _sort_gaussian_torch
except ImportError:
    try:
        import cupy as cp
        print("Detected cupy installed, will use cupy as sorting backend")
        _sort_gaussian = _sort_gaussian_cupy
    except ImportError:
        _sort_gaussian = _sort_gaussian_cpu


class GaussianRenderBase:
    def __init__(self):
        self.gaussians = None  # Expected to be a GaussianSet instance
        self._reduce_updates = True

    @property
    def reduce_updates(self):
        return self._reduce_updates

    @reduce_updates.setter
    def reduce_updates(self, val):
        self._reduce_updates = val
        self.update_vsync()

    def update_vsync(self):
        print("VSync is not supported")

    def update_gaussian_data(self, gaussianset):
        raise NotImplementedError()
    
    def sort_and_update(self):
        raise NotImplementedError()

    def set_scale_modifier(self, modifier: float):
        raise NotImplementedError()
    
    def set_render_mode(self, mod: int):
        raise NotImplementedError()
    
    def update_camera_pose(self):
        raise NotImplementedError()

    def update_camera_intrin(self):
        raise NotImplementedError()
    
    def draw(self):
        raise NotImplementedError()
    
    def set_model_matrix(self, model_mat):
        raise NotImplementedError()
    
    def set_render_resolution(self, w, h):
        raise NotImplementedError()


class OpenGLRenderer(GaussianRenderBase):
    def __init__(self, w, h, world_settings):
        super().__init__()
        gl.glViewport(0, 0, w, h)
        self.program = util.load_shaders('./ui/shaders/gau_vert.glsl', './ui/shaders/gau_frag.glsl')

        # Vertex data for a quad
        self.quad_v = np.array([
            -1,  1,
             1,  1,
             1, -1,
            -1, -1
        ], dtype=np.float32).reshape(4, 2)
        self.quad_f = np.array([
            0, 2, 1,
            0, 3, 2
        ], dtype=np.uint32).reshape(2, 3)
        
        # Load quad geometry into a VAO.
        vao, buffer_id = util.set_attributes(self.program, ["position"], [self.quad_v])
        util.set_faces_to_vao(vao, self.quad_f)
        self.vao = vao
        self.gau_bufferid = None
        self.index_bufferid = None
        
        # OpenGL settings.
        gl.glEnable(gl.GL_CULL_FACE)
        # gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        self.update_vsync()
        # Save a reference to the world_settings so that the camera is accessed through it.
        self.world_settings = world_settings

    def update_vsync(self):
        if wglSwapIntervalEXT is not None:
            wglSwapIntervalEXT(1 if self.reduce_updates else 0)
        else:
            print("VSync is not supported")

    def update_gaussian_data(self, gaussianset):
        self.gaussians = gaussianset
        # Obtain the flattened representation from the GaussianSet.
        gaussian_data = gaussianset.flat()
        
        self.gau_bufferid = util.set_storage_buffer_data(
            self.program,
            "gaussian_data",
            gaussian_data, 
            bind_idx=0,
            buffer_id=self.gau_bufferid
        )
        # Use the sh_dim property from GaussianSet.
        util.set_uniform_1int(self.program, gaussianset.sh_dim, "sh_dim")

    def sort_and_update(self):
        camera = self.world_settings.world_camera
        time_start = util.get_time()
        index = _sort_gaussian(self.gaussians, camera.get_view_matrix())
        time_end = util.get_time()
        util.logger.debug(f"Sorting time: {time_end - time_start:.3f} s")
        self.index_bufferid = util.set_storage_buffer_data(
            self.program,
            "gaussian_order",
            index, 
            bind_idx=1,
            buffer_id=self.index_bufferid
        )
        
    def set_scale_modifier(self, modifier):
        util.set_uniform_1f(self.program, modifier, "scale_modifier")

    def set_render_mode(self, mod: int):
        util.set_uniform_1int(self.program, mod, "render_mod")

    def set_render_resolution(self, w, h):
        gl.glViewport(0, 0, w, h)

    def update_camera_pose(self):
        # Retrieve the camera solely through the world_settings object.
        camera = self.world_settings.world_camera
        view_mat = camera.get_view_matrix()
        util.set_uniform_mat4(self.program, view_mat, "view_matrix")
        util.set_uniform_v3(self.program, camera.position, "cam_pos")

    def update_camera_intrin(self):
        camera = self.world_settings.world_camera
        proj_mat = camera.get_project_matrix()
        util.set_uniform_mat4(self.program, proj_mat, "projection_matrix")
        util.set_uniform_v3(self.program, camera.get_htanfovxy_focal(), "hfovxy_focal")

    def set_model_matrix(self, model_mat):
        util.set_uniform_mat4(self.program, model_mat, "model_matrix")

    def draw(self):
        gl.glUseProgram(self.program)
        gl.glBindVertexArray(self.vao)
        num_gau = len(self.gaussians)
        gl.glDrawElementsInstanced(
            gl.GL_TRIANGLES,
            len(self.quad_f.reshape(-1)),
            gl.GL_UNSIGNED_INT,
            None,
            num_gau
        )
