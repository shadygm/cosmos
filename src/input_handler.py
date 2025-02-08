import glfw
import util
import sys


class InputHandler:
    def __init__(self, window, world_settings):
        self.window = window
        self.log = util.get_logger()
        self.init_callbacks()
        self.world_settings = world_settings
        self.last_time = glfw.get_time()
    def init_callbacks(self):
        self.log.info("Initializing callbacks")
        return
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
