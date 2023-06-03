#================================================================================#
# File: miscellaneous.py
# Created Date: 23-05-2023 | 18:11:25
# Author: Hereiti
#================================================================================
# Last Modified: 04-06-2023 | 01:05:45
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Imports
#================================================================================#
import logging
import os

#================================================================================#
# Local Application Imports
#================================================================================#
from modules import icons, images, edits, utils

#================================================================================#
# Functions
#================================================================================#
def connect_buttons(app: 'classes.MainWindow.MainWindow') -> None:
    """Connect the signals of buttons to their respective functions.

    Args:
        app (MainWindow.MainWindow): The main application window.

    """
    # Connect buttons signals to their respective functions
    app.buttons["New"].clicked.connect(lambda: icons.new(app))
    app.buttons["Open"].clicked.connect(lambda: icons.load(app, None, True, True))
    app.buttons["Add After"].clicked.connect(lambda: icons.sheet(app))
    app.buttons["Folder"].clicked.connect(lambda: icons.folder(app))
    app.buttons["Save Selected"].clicked.connect(lambda: images.save_selected(app))
    app.buttons["Save Separately"].clicked.connect(lambda: images.save_individually(app))
    app.buttons["Save All"].clicked.connect(lambda: images.save_all(app))

def connect_actions(app : 'classes.MainWindow.MainWindow') -> None:
    """Connect actions to their respective functions in the MainWindow.

    Args:
        app (MainWindow.MainWindow): The instance of the main application window.

    Returns:
        None
    """

    # Connect action triggered signal to their respective functions
    for action in app.file_menu.actions():
        if action.text() == "New":
            action.setShortcut("Ctrl+N")
            action.triggered.connect(lambda: icons.new(app))

        if action.text() == "Open":
            action.setShortcut("Ctrl+O")
            action.triggered.connect(lambda: icons.load(app))

        if action.text() == "Save All":
            action.setShortcut("Ctrl+S")
            action.triggered.connect(lambda: images.save_all(app))

        if action.text() == "Save Selected":
            action.setShortcut("Ctrl+Shift+S")
            action.triggered.connect(lambda: images.save_selected(app))

        if action.text() == "Save Separately":
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

    for action in app.view_menu.actions():
        if action.text() == "Theme":
            action.triggered.connect(lambda: utils.images_background(app))

        if action.text() == "Icon Set":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Type", "Icon Set"))

        if action.text() == "Tileset":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Type", "Tileset"))

        if action.text() == "16x16":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "16x16"))

        if action.text() == "24x24":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "24x24"))

        if action.text() == "32x32":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "32x32"))

        if action.text() == "48x48":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Cell Size", "48x48"))

        if action.text() == "A1-A2":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset", "A1-A2"))

        if action.text() == "A3":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset", "A3"))

        if action.text() == "A4":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset", "A4"))

        if action.text() == "A5":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset", "A5"))

        if action.text() == "B-E":
            action.triggered.connect(lambda: utils.config_changes_restart(app, "Tileset", "B-E"))

    for action in app.help_menu.actions():
        if action.text() == "About":
            action.triggered.connect(lambda: utils.about())

def connect_edits_widget(app: 'classes.MainWindow.MainWindow', check: bool = False) -> None:
    """
    Enable or disable offset buttons and sliders in the MainWindow.

    Args:
        app (MainWindow.MainWindow): The instance of the main application window.
        check (bool, optional): Flag indicating whether to enable or disable the widgets. Defaults to False.

    Returns:
        None
    """

    if check:
        # Enable offset buttons
        for button in app.offset_buttons:
            app.offset_buttons[button].setEnabled(True)

        # Enable sliders
        for slider in app.sliders:
            app.sliders[slider].setEnabled(True)

    else:
        # Disable offset buttons
        for button in app.offset_buttons:
            app.offset_buttons[button].setEnabled(False)

        # Disable sliders
        for slider in app.sliders:
            app.sliders[slider].setEnabled(False)

def delete_temp_files(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Delete temporary files and log files associated with the application.

    Args:
        app (MainWindow.MainWindow): The instance of the main application window.

    Returns:
        None
    """

    # Delete temporary files
    for file in app.temp_files:
        if os.path.exists(file):
            os.remove(file)

    # Shutdown the logging system
    logging.shutdown()

    # Remove empty log file
    log_folder = os.path.expanduser("~\\OneDrive\\Documents\\Hereiti - Set Manager\\logs")
    log_file = os.path.join(log_folder, app.log_name)
    if os.path.isfile(log_file) and os.path.getsize(log_file) == 0:
        os.remove(log_file)
