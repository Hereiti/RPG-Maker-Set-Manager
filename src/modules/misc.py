#================================================================================#
# File: misc.py
# Created Date: 06-06-2023 | 11:46:09
# Author: Hereiti
#================================================================================
# Last Modified: 08-06-2023 | 11:08:53
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
import logging
import os

#================================================================================#
# Local imports
#================================================================================#
from modules import edits
from modules import icons
from modules import images
from modules import utils

#================================================================================#
# Functions
#================================================================================#
def connect_buttons(app: 'classes.main_window.MainWindow') -> None:
    """Connect the signals of buttons to their respective functions.

    Args:
        - app: The main application window.

    """
    # Connect buttons signals to their respective functions
    app.buttons["New"].clicked.connect(lambda: icons.new(app))
    app.buttons["Open"].clicked.connect(lambda: icons.load(app, None, True, True))
    app.buttons["Add After"].clicked.connect(lambda: icons.add_after(app))
    app.buttons["Folder"].clicked.connect(lambda: icons.folder(app))
    app.buttons["Save Highlighted Cell"].clicked.connect(lambda: images.save_selected(app))
    app.buttons["Save Individually Each Cell"].clicked.connect(lambda: images.save_separately(app))
    app.buttons["Save All Together"].clicked.connect(lambda: images.save_all(app))

    if app.animation_buttons:
        app.animation_buttons["Play"].clicked.connect(lambda: images.play_animations(app))
        app.animation_buttons["Stop"].clicked.connect(lambda: images.stop_animations(app))

    app.edits_buttons["Offset"].clicked.connect(lambda: edits.change_offset(app))
    app.edits_buttons["Hue"].clicked.connect(lambda: edits.change_hue(app))
    app.edits_buttons["Saturation"].clicked.connect(lambda: edits.change_saturation(app))
    app.edits_buttons["Brightness"].clicked.connect(lambda: edits.change_brightness(app))
    app.edits_buttons["Red"].clicked.connect(lambda: edits.change_color(app, "red"))
    app.edits_buttons["Green"].clicked.connect(lambda: edits.change_color(app, "green"))
    app.edits_buttons["Blue"].clicked.connect(lambda: edits.change_color(app, "blue"))

def connect_actions(app: 'classes.main_window.MainWindow') -> None:
    """
    Connect actions to their respective functions

    Args:
        - app: The instance of the main application window.
    """
    # Connect action triggered signal to their respective functions
    for action in app.file_menu.actions():
        if action.text() == "New":
            action.setShortcut("Ctrl+N")
            action.triggered.connect(lambda: icons.new(app))

        if action.text() == "Open":
            action.setShortcut("Ctrl+O")
            action.triggered.connect(lambda: icons.load(app))

        if action.text() == "Save All Together":
            action.setShortcut("Ctrl+S")
            action.triggered.connect(lambda: images.save_all(app))

        if action.text() == "Save Highlighted Cell":
            action.setShortcut("Ctrl+Shift+S")
            action.triggered.connect(lambda: images.save_selected(app))

        if action.text() == "Save Individually Each Cell":
            action.setShortcut("Ctrl+Alt+S")
            action.triggered.connect(lambda: images.save_individually(app))

        if action.text() == "Exit":
            action.setShortcut("Alt+F4")
            action.triggered.connect(lambda: app.destroy())

    for action in app.edit_menu.actions():
        if action.text() == "Undo":
            action.setShortcut("Ctrl+Z")
            action.triggered.connect(lambda: edits.undo(app))

        if action.text() == "Redo":
            action.setShortcut("Ctrl+Y")
            action.triggered.connect(lambda: edits.redo(app))

        if action.text() == "Cut":
            action.setShortcut("Ctrl+X")
            action.triggered.connect(lambda: edits.cut(app))

        if action.text() == "Copy":
            action.setShortcut("Ctrl+C")
            action.triggered.connect(lambda: edits.copy(app))

        if action.text() == "Paste":
            action.setShortcut("Ctrl+V")
            action.triggered.connect(lambda: edits.paste(app))

    for action in app.help_menu.actions():
        if action.text() == "About":
            action.triggered.connect(lambda: utils.about())
        if action.text() == "Report Issue":
            action.triggered.connect(lambda: utils.report_issue())

    for action in app.view_menu.actions():
        if action.text() == "Theme":
            action.triggered.connect(lambda: utils.images_background(app))

    for action in app.type_menu.actions():
        if action.text() == "Icons":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Type", "Icons"))

        if action.text() == "Tileset":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Type", "Tileset"))

        if action.text() == "Faces":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Type", "Faces"))

        if action.text() == "SV Actor":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Type", "SV Actor"))

        if action.text() == "Sprites":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Type", "Sprites"))

    for action in app.size_menu.actions():
        if action.text() == "16x16":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "16x16"))

        if action.text() == "24x24":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "24x24"))

        if action.text() == "32x32":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "32x32"))

        if action.text() == "48x48":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "48x48"))

        if action.text() == "64x64":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "64x64"))

        if action.text() == "96x96":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "96x96"))

        if action.text() == "128x128":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "128x128"))

        if action.text() == "160x160":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "160x160"))

        if action.text() == "192x192":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "192x192"))

    for action in app.tile_menu.actions():
        if action.text() == "A1-A2":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset Sheet", "A1-A2"))

        if action.text() == "A3":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset Sheet", "A3"))

        if action.text() == "A4":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset Sheet", "A4"))

        if action.text() == "A5":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset Sheet", "A5"))

        if action.text() == "B-E":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset Sheet", "B-E"))

    for action in app.creator_menu.actions():
        if action.text() == "Holder":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Creator Compatibility", "Holder"))
        if action.text() == "None":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Creator Compatibility", "None"))

def delete_temp_files(app: 'classes.main_window.MainWindow') -> None:
    """
    Delete temporary files and log files associated with the application.

    Args:
        app (MainWindow.MainWindow): The instance of the main application window.
    """
    # Delete temporary files
    for file in app.temp:
        if os.path.exists(file):
            os.remove(file)

    # Shutdown the logging system
    logging.shutdown()

    # Remove empty log file
    log_folder = os.path.expanduser("~\\OneDrive\\Documents\\Hereiti - Set Manager\\logs")
    log_file = os.path.join(log_folder, app.log_name)
    if os.path.isfile(log_file) and os.path.getsize(log_file) == 0:
        os.remove(log_file)
