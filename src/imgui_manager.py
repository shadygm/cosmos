import imgui
import tkinter as tk
from tkinter import filedialog

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the root window to avoid it appearing
    file_path = filedialog.askopenfilename(title="Choose a PLY file", filetypes=[("PLY Files", "*.ply")])
    root.quit()
    root.destroy()  
    return file_path

def main_ui(world_settings):
    # Create the main menu bar
    if imgui.begin("Cosmos", True):
        imgui.text(f"FPS: {imgui.get_io().framerate:.1f}")
        imgui.text(f"Num of Gauss: {world_settings.get_num_gaussians()}")

        if imgui.button("Load PLY"):
            file_path = open_file_dialog()
            if file_path:
                world_settings.load_ply(file_path)

        imgui.end()
