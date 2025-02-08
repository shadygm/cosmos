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

    global window
    window = glfw.create_window(
        world_camera.w, world_camera.h, window_name, None, None
    )

    glfw.make_context_current(window)
    glfw.swap_interval(0)

    if not window:
        log.error("Could not initialize Window")
        glfw.terminate()
    return window


def game_loop(window, glfw_renderer):
    while not glfw.window_should_close(window):
        glfw.poll_events()
        gl.glClearColor(0, 0, 0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
        world_settings.input_handler.check_inputs()

        imgui.new_frame()


        imgui_manager.main_ui(world_settings=world_settings)

        imgui.render()
        glfw_renderer.render(imgui.get_draw_data())
        glfw_renderer.process_inputs()
        glfw.swap_buffers(window)
        
    glfw.terminate()


def main():
    imgui.create_context()
    window = impl_glfw_init()

    glfw_renderer = GlfwRenderer(window)
    input_handler = InputHandler(window, world_settings)
    world_settings.input_handler = input_handler

    # Backend GS renderer

    game_loop(window, glfw_renderer)

if __name__ == "__main__":
    global log, input_handler
    log = util.get_logger()
    main()