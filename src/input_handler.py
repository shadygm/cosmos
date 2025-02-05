import glfw
import util

def working_log(window, xpos, ypos):
    """Callback function for mouse movement."""
    log = util.get_logger()
    log.info(f"Mouse moved to ({xpos}, {ypos})")

class InputHandler:
    def __init__(self, window):
        self.window = window
        self.log = util.get_logger()
        self.init_callbacks()

    def init_callbacks(self):
        """Initialize GLFW callbacks."""
        glfw.set_cursor_pos_callback(self.window, working_log)
