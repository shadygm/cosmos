import imgui
import tkinter as tk
from tkinter import filedialog

world_settings = None
type_visualization = ["Gaussian Ball", "Flat Ball", "Billboard", "Depth", "SH:0", "SH:0~1", "SH:0~2", "SH:0~3 (default)"]
show_cam_window = False
show_param_window = True
def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the root window to avoid it appearing
    file_path = filedialog.askopenfilename(title="Choose a PLY file", filetypes=[("PLY Files", "*.ply")])
    root.quit()
    root.destroy()  
    return file_path

def load_file():
    if imgui.button("Load PLY"):
            file_path = open_file_dialog()
            if file_path:
                world_settings.load_ply(file_path)

def parameters():
    imgui.text("Parameters:")

    # Sorting
    if imgui.button("Sort and Update"):
        world_settings.gauss_renderer.sort_and_update()
    imgui.same_line()
    changed, world_settings.auto_sort = imgui.checkbox("Auto-sort", world_settings.auto_sort)

    # Visualization type
    changed, mode = imgui.combo("Visualization Type", world_settings.render_mode, type_visualization)
    if changed:
        world_settings.update_render_mode(mode)

def menu_bar():
    global show_cam_window, show_param_window
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("Camera", True):
            clicked, show_cam_window = imgui.menu_item("Camera Settings", None, show_cam_window)
            clicked, show_param_window = imgui.menu_item("Parameters", None, show_param_window)
        
            imgui.end_menu()
        imgui.end_main_menu_bar()
def param_window():
    if imgui.begin("Cosmos", True):
        imgui.text(f"FPS: {imgui.get_io().framerate:.1f}")
        imgui.text(f"Num of Gauss: {world_settings.get_num_gaussians()}")

        load_file()
        parameters()

        imgui.end()
def cam_window():
    if imgui.begin("Camera Settings", True):
        imgui.text("Bleh")
        
        imgui.end()

def main_ui(this_world_settings):
    global world_settings
    if world_settings is None:
        world_settings = this_world_settings

    # Create the main menu bar
    menu_bar()
    if show_cam_window:
        cam_window()
    if show_param_window:
        param_window()
    
