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
    

    def check_inputs(self):
        # Time-based to make it frame-rate independent
        curr_time = glfw.get_time()
        delta = curr_time - self.last_time
        self.last_time = curr_time


        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS: # Forward
            self.world_settings.process_translation(0, delta)
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS: # Left
            self.world_settings.process_translation(-delta, 0)
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS: # Backward
            self.world_settings.process_translation(0, -delta)
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS: # Right
            self.world_settings.process_translation(delta, 0)