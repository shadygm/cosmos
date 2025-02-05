import imgui

def main_ui():
    # Create the main menu bar
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("Cosmos", True):
            imgui.menu_item("Example Item")
            imgui.end_menu()
        imgui.end_main_menu_bar()

    # Create a new window to display text
    imgui.begin("Example Window")  # Window title
    imgui.text_colored("This is white text", 1.0, 1.0, 1.0, 1.0)  # Display white text
    imgui.end()

    