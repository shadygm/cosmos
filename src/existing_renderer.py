from fast_gauss import GaussianRasterizationSettings, GaussianRasterizer
from camera import Camera


def setup(camera: Camera):
    width = camera.width
    height = camera.height
    fovy = camera.fovy
    znear = camera.near
    zfar = camera.far

    view_matrix = camera.get_view_matrix()
    projection_matrix = camera.get_project_matrix()

    settings = GaussianRasterizationSettings(
        width, height, fovy, znear, zfar, view_matrix, projection_matrix
    )

    rasterizer = GaussianRasterizer(settings)

    return rasterizer

