import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import imgui
import numpy as np
import imageio
import os
import sys
from loguru import logger
import logging
from camera import Camera
from input_handler import InputHandler
import util
import imgui_manager
from worldsettings import WorldSettings



# Make a Camera object
world_settings = WorldSettings()
world_camera = world_settings.world_camera
def impl_glfw_init():
    window_name = "Cosmos"

    if not glfw.init():
        log.error("Could not initialize GLFW")
        exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    global window
    window = glfw.create_window(
        world_camera.w, world_camera.h, window_name, None, None
    )

    glfw.make_context_current(window)
    glfw.swap_interval(0)

    if not window:
        log.error("Could not initialize Window")
        glfw.terminate()
        exit(1)
    return window

def update_camera_pose_lazy():
    if world_camera.dirty_pose:
        world_settings.gauss_renderer.update_camera_pose()
        world_camera.dirty_pose = False
def update_camera_intrin_lazy():
    if world_settings.world_camera.dirty_intrinsic:
        world_settings.gauss_renderer.update_camera_intrin()
        world_settings.world_camera.dirty_intrinsic = False

def processFrames():
    update_camera_pose_lazy()
    update_camera_intrin_lazy()
    if world_settings.auto_sort:
        world_settings.gauss_renderer.sort_and_update()


def game_loop(window, glfw_renderer):
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw_renderer.process_inputs()

        gl.glClearColor(0, 0, 0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
        world_settings.input_handler.check_inputs()

        imgui.new_frame()

        processFrames()

        imgui_manager.main_ui(world_settings=world_settings)
        world_settings.gauss_renderer.draw()

        imgui.render()
        glfw_renderer.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
        
    glfw.terminate()


def main():
    imgui.create_context()
    window = impl_glfw_init()

    glfw_renderer = GlfwRenderer(window)
    input_handler = InputHandler(window, world_settings)
    world_settings.input_handler = input_handler

    # Backend GS renderer
    world_settings.create_gaussian_renderer()
    world_settings.update_activated_render_state()
    game_loop(window, glfw_renderer)

if __name__ == "__main__":
    global log, input_handler
    log = util.get_logger()
    main()