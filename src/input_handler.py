import glfw
import util
import sys
import imgui
import numpy as np

class InputHandler:
    def __init__(self, window, world_settings):
        self.window = window
        self.log = util.get_logger()
        self.init_callbacks()
        self.world_settings = world_settings
        self.last_time = glfw.get_time()
    def init_callbacks(self):
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_window_size_callback(self.window, self.window_resize_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)
        self.log.info("Initializing callbacks")
        return
    
    def mouse_button_callback(self, window, button, action, mods):
        if imgui.get_io().want_capture_mouse:
            return
        pressed = action == glfw.PRESS
        self.world_settings.world_camera.is_leftmouse_pressed = button == glfw.MOUSE_BUTTON_LEFT and pressed
        self.world_settings.world_camera.is_rightmouse_pressed = button == glfw.MOUSE_BUTTON_RIGHT and pressed

    def cursor_pos_callback(self, window, xpos, ypos):
        if imgui.get_io().want_capture_mouse:
            self.world_settings.world_camera.is_left_mouse_pressed = False
            self.world_settings.world_camera.is_right_mouse_pressed = False
        self.world_settings.world_camera.process_mouse(xpos, ypos)
    
    def scroll_callback(self, window, xoffset, yoffset):
        self.world_settings.world_camera.process_scroll(xoffset, yoffset)

    def window_resize_callback(self, window, width, height):
        self.world_settings.world_camera.w = width
        self.world_settings.world_camera.h = height
        self.world_settings.gauss_renderer.set_render_resolution(width, height)

    def check_inputs(self):
        # Time-based to make it frame-rate independent
        curr_time = glfw.get_time()
        delta = curr_time - self.last_time
        self.last_time = curr_time

        # View transformations
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS: # Forward
            self.world_settings.process_translation(0, delta)
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS: # Left
            self.world_settings.process_translation(-delta, 0)
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS: # Backward
            self.world_settings.process_translation(0, -delta)
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS: # Right
            self.world_settings.process_translation(delta, 0)

        # Model transformations
        if glfw.get_key(self.window, glfw.KEY_I) == glfw.PRESS: # Model forward
            self.world_settings.process_model_translation(0, -delta)
        if glfw.get_key(self.window, glfw.KEY_J) == glfw.PRESS: # Model left
            self.world_settings.process_model_translation(delta, 0)
        if glfw.get_key(self.window, glfw.KEY_K) == glfw.PRESS: # Model backward
            self.world_settings.process_model_translation(0, delta)
        if glfw.get_key(self.window, glfw.KEY_L) == glfw.PRESS:
            self.world_settings.process_model_translation(-delta, 0)
            
