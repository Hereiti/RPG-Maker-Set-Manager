#!/usr/bin/env python
"""misc.py"""
import os
from PySide6.QtGui import QDesktopServices
from modules import files
from modules import grid_manager
from modules import image_manipulation
from modules import utils
from creator import holder


def connect_buttons(app):
    """
    Connect the signals of buttons to their respective functions.

    Args:
        - app: The main application window.
    """
    # Connect buttons signals to their respective functions
    app.toolbar_actions["New"].triggered.connect(
        lambda: grid_manager.clear_main_view(app))
    app.toolbar_actions["Open"].triggered.connect(
        lambda: grid_manager.load(app, None, True, True, None))
    app.toolbar_actions["Add After"].triggered.connect(
        lambda: grid_manager.add_after(app))
    app.toolbar_actions["Load Folder"].triggered.connect(
        lambda: grid_manager.load_folder(app))
    app.toolbar_actions["Save Highlighted Cell(s)"].triggered.connect(
        lambda: files.save_highlighted_cell(app))
    app.toolbar_actions["Save Individually Each Cell"].triggered.connect(
        lambda: files.save_individually_each_cell(app))
    app.toolbar_actions["Save All Together"].triggered.connect(
        lambda: files.save_all_together(app))

    app.adjustment_toolbar_actions["Offset"].triggered.connect(
        lambda: app.frames["Offset"].show())
    app.adjustment_toolbar_actions["Resize"].triggered.connect(
        lambda: app.frames["Resize"].show())
    app.adjustment_toolbar_actions["Rotate"].triggered.connect(
        lambda: app.frames["Rotate"].show())
    app.adjustment_toolbar_actions["HSV"].triggered.connect(
        lambda: app.frames["HSV"].show())
    app.adjustment_toolbar_actions["RGB"].triggered.connect(
        lambda: app.frames["RGB"].show())

    app.adjustment_toolbar_actions["Play"].triggered.connect(
        lambda: image_manipulation.play_animation(app))

    app.adjustment_toolbar_actions["Stop"].triggered.connect(
        lambda: image_manipulation.stop_animation(app))

    app.adjustment_toolbar_actions["Flip Horizontally"].triggered.connect(
        lambda: image_manipulation.flip_image(app, "Horizontal"))
    app.adjustment_toolbar_actions["Flip Vertically"].triggered.connect(
        lambda: image_manipulation.flip_image(app, "Vertical"))

    app.buttons["Hue"].clicked.connect(
        lambda: image_manipulation.change_hue(app))
    app.buttons["Saturation"].clicked.connect(
        lambda: image_manipulation.change_saturation(app))
    app.buttons["Value"].clicked.connect(
        lambda: image_manipulation.change_value(app))

    app.buttons["Red"].clicked.connect(
        lambda: image_manipulation.change_color(app, "Red"))
    app.buttons["Green"].clicked.connect(
        lambda: image_manipulation.change_color(app, "Green"))
    app.buttons["Blue"].clicked.connect(
        lambda: image_manipulation.change_color(app, "Blue"))

    app.buttons["Change Offset"].clicked.connect(
        lambda: image_manipulation.change_offset(app))


def connect_actions(app):
    """
    Connect actions to their respective functions.

    Args:
        - app: The main application window.
    """
    # Connect action triggered signal to their respective functions
    for action in app.file_menu.actions():
        if action.text() == "New":
            action.setShortcut("Ctrl+N")
            action.triggered.connect(lambda: grid_manager.new(app))

        if action.text() == "Open":
            action.setShortcut("Ctrl+O")
            action.triggered.connect(lambda: grid_manager.load(app))

        if action.text() == "Save All Together":
            action.setShortcut("Ctrl+S")
            action.triggered.connect(lambda: files.save_all_together(app))

        if action.text() == "Save Highlighted Cell":
            action.setShortcut("Ctrl+Shift+S")
            action.triggered.connect(lambda: files.save_highlighted_cell(app))

        if action.text() == "Save Individually Each Cell":
            action.setShortcut("Ctrl+Alt+S")
            action.triggered.connect(
                lambda: files.save_individually_each_cell(app))

        if action.text() == "Exit":
            action.setShortcut("Alt+F4")
            action.triggered.connect(lambda: app.destroy())

    for action in app.edit_menu.actions():
        if action.text() == "Undo":
            action.setShortcut("Ctrl+Z")
            action.triggered.connect(lambda: image_manipulation.undo(app))

        if action.text() == "Redo":
            action.setShortcut("Ctrl+Y")
            action.triggered.connect(lambda: image_manipulation.redo(app))

        if action.text() == "Cut":
            action.setShortcut("Ctrl+X")
            action.triggered.connect(lambda: image_manipulation.cut(app))

        if action.text() == "Copy":
            action.setShortcut("Ctrl+C")
            action.triggered.connect(lambda: image_manipulation.copy(app))

        if action.text() == "Paste":
            action.setShortcut("Ctrl+V")
            action.triggered.connect(lambda: image_manipulation.paste(app))

    for action in app.help_menu.actions():
        if action.text() == "About":
            action.triggered.connect(lambda: utils.about())
        if action.text() == "Report Issue":
            action.triggered.connect(lambda: utils.report_issue())
        if action.text() == "Contributors":
            action.triggered.connect(lambda: utils.contributors())
        if action.text() == "Supporters":
            action.triggered.connect(lambda: utils.supporters())
        if action.text() == "Releases Notes":
            action.triggered.connect(
                lambda: utils.show_releases_notes(app))
        if action.text() == "Check for Update...":
            action.triggered.connect(
                lambda: utils.check_update(f"v{os.getenv('VERSION')}-alpha"))

    for action in app.view_menu.actions():
        if action.text() == "Theme":
            action.triggered.connect(lambda: utils.images_background(app))

        if action.text() == "Custom Grid":
            action.triggered.connect(lambda: grid_manager.custom_grid(app))

    for action in app.sub_menus["Presets"].actions():
        if action.text() == "Icons":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Type", "Icons"))

        if action.text() == "Tileset":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Type", "Tileset"))

        if action.text() == "Faces":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Type", "Faces"))

        if action.text() == "SV Actor":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Type", "SV Actor"))

        if action.text() == "Sprites":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Type", "Sprites"))

        if action.text() == "States":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Type", "States"))

        if action.text() == "Weapons":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Type", "Weapons"))

        if action.text() == "Balloons":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Type", "Balloons"))

    for action in app.sub_menus["Cell Size"].actions():
        if action.text() == "16x16":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Cell Size", "16x16"))

        if action.text() == "24x24":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Cell Size", "24x24"))

        if action.text() == "32x32":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Cell Size", "32x32"))

        if action.text() == "48x48":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Cell Size", "48x48"))

        if action.text() == "Custom Cell Size":
            action.triggered.connect(
                lambda: grid_manager.custom_cell_size(app))

    for action in app.sub_menus["Tilesets"].actions():
        if action.text() == "A1-A2":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Tileset Sheet", "A1-A2"))

        if action.text() == "A3":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Tileset Sheet", "A3"))

        if action.text() == "A4":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Tileset Sheet", "A4"))

        if action.text() == "A5":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Tileset Sheet", "A5"))

        if action.text() == "B-E":
            action.triggered.connect(
                lambda: utils.config_changes_restart(app, "Tileset Sheet", "B-E"))

    for action in app.creator_menus["Holder"].actions():
        if action.text() == "SV Actor | 192x160":
            action.triggered.connect(
                lambda: holder.holder_presets(app, "SV Actor | 192x160"))

        if action.text() == "SV Actor | 160x160":
            action.triggered.connect(
                lambda: holder.holder_presets(app, "SV Actor | 160x160"))

        if action.text() == "Load Weapons Folder":
            action.triggered.connect(
                lambda: holder.tree_view(app)
            )

        if action.text() == "Format Current Sheet to MZ":
            action.triggered.connect(
                lambda: holder.format_current_grid_to_mz(app)
            )

        if action.text() == "Format Whole Folder to MZ":
            action.triggered.connect(
                lambda: holder.format_folder_to_mz(app)
            )

        if action.text() == "Open Holder's itch.io Page":
            action.triggered.connect(
                lambda: QDesktopServices.openUrl("https://holder-anibat.itch.io"))


def delete_temp_files(app):
    """
    Delete temporary files.

    Args:
        - app: The main application window.
    """
    # Delete temporary files
    for file in app.temp:
        if os.path.exists(file):
            os.remove(file)
