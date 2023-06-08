#================================================================================#
# File: utils.py
# Created Date: 05-06-2023 | 18:02:30
# Author: Hereiti
#================================================================================
# Last Modified: 08-06-2023 | 13:59:04
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built+in imports
#================================================================================#
import re
import sys

from typing import List, Optional, Tuple

#================================================================================#
# Third-party imports
#================================================================================#
from PySide6.QtCore import QDir, QPointF, QRectF
from PySide6.QtGui import QAction, QImage, QMouseEvent
from PySide6.QtWidgets import QColorDialog, QDialog, QFileDialog, QGraphicsPixmapItem, QMainWindow, QMenu, QMessageBox

from github import Github

#================================================================================#
# Local imports
#================================================================================#
from classes import graphics_item
from classes import main_window
from classes import widgets

from modules import config
from modules import images
from modules import maths
from modules import misc

#================================================================================#
# Functions
#================================================================================#
def click_cell(event: QMouseEvent, app: 'classes.main_window.MainWindow') -> None:
    """
    Handle the click event on a cell.

    This function is called when a cell is clicked in the main view.

    Args:
        - event (QMouseEvent): The mouse event triggered by the click
        - app ('classes.main_window.MainWindow'): The main window
            application instance.
    """
    # Retrieve main_view and cell_size from the app
    _main_view = app.main_view
    _cell_size = app.cell_size

    # Map the event position to scene coordinates
    _scene_pos = _main_view.mapToScene(event.pos())
    _x, _y = _scene_pos.x(), _scene_pos.y()

    # Calculate the cell index and origin
    _cell_index = maths.index(_x, _y)
    _cell_origin = maths.origin(_cell_index)

    # Check if the click is out of bounds
    _limit = maths.origin((maths.grid_col() - 1, maths.grid_row() - 1))
    if any(_coord < 0 or _coord > limit for _coord, limit, in zip(_cell_origin, _limit)):
        return

    # Check if there is already a highlight or not
    if _main_view.highlight_selected[0] is None:
        _main_view.highlight_selected = [graphics_item.Highlight("red", _cell_size), _cell_index]
        _main_view.scene.addItem(_main_view.highlight_selected[0])
        _main_view.highlight_selected[0].setZValue(2)
        _main_view.highlight_selected[0].setOpacity(0.5)

    # Set the position and index of the highlight item
    _main_view.highlight_selected[0].setPos(*_cell_origin)
    _main_view.highlight_selected[0].visible = True
    _main_view.highlight_selected[1] = _cell_index

    if app.animation[1]:
        images.play_animations(app)

    _num = _cell_index[1] * 16 + _cell_index[0]
    app.labels["Index"].setText(f"● [{_cell_index[0]}:{_cell_index[1]}] - Cell n°{_num} ●")
    images.zoom(app, images.get_image_at(app, _cell_index))

def prompt_file(app: 'classes.main_window.MainWindow') -> Optional[QImage]:
    """
    Open a file dialog to select a PNG file and return it as a QImage

    Args:
        - app: The instance of the MainWindow class

    Returns:
        The QImage of the selected file, otherwise None.
    """
    # Open the file dialog
    file_path, _ = QFileDialog.getOpenFileName(app, "Open File", "", "Image Files (*.png *.jpg *.jpeg *.gif)")

    if file_path:
        return QImage(file_path)

    return None

def prompt_folder(app: 'classes.main_window.MainWindow') -> Optional[Tuple[QDir, List[str]]]:
    """
    Open a folder dialog to select a folder

    Returns:
        - A tuple containing the directory object and a list of PNG
            file names in the selected folder or None if no folder is
            selected
    """
    # Open the folder dialog
    _folder_path = QFileDialog.getExistingDirectory(None, "Select Folder", "/")
    _dir = QDir(_folder_path)

    # Set the filter and name filter to include only PNG files
    _dir.setFilter(QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
    _dir.setNameFilters(["*.png", "*.jpg", "*.jpeg", "*.gif"])

    # Return the directory object and a list of PNG file names in the folder
    return (_dir, _dir.entryList())

def numerical_sort_key(_string: str) -> int:
    """Key function for sorting strings with two numbers.

    This function extracts two numerical parts from a string and combines them into a single integer.
    It is intended to be used as the key function in sorting operations to achieve sorting based on two numbers.

    Args:
        _string (str): The input string.

    Returns:
        int: The combined numerical value of the two parts, or a default value if no numerical parts are found.
    """
    # Extract numerical parts from the string
    matches = re.findall(r'\d+', _string)
    if len(matches) >= 2:
        number1 = int(matches[0])
        number2 = int(matches[1])
        combined_number = (number1 * 100) + number2  # Adjust the multiplier as per your requirements
        return combined_number

    # Return a default value that can be compared
    return sys.maxsize

def highlight_index(app: 'classes.main_window.MainWindow', _index: Tuple[int, int]) -> None:
    """
    Highlights the given index in the main view.

    Args:
        - app (classes.MainWindow.MainWindow): The main window application instance.
        - _index: The index of the selected cell.
    """
    if app.main_view.highlight_selected[0] is None:
        app.main_view.highlight_selected = [graphics_item.Highlight("red", app.cell_size), _index]
        app.main_view.scene.addItem(app.main_view.highlight_selected[0])

    app.main_view.highlight_selected[0].setZValue(2)
    app.main_view.highlight_selected[0].setOpacity(0.5)
    app.main_view.highlight_selected[0].setPos(*maths.origin(_index))
    app.main_view.highlight_selected[1] = _index

    images.zoom(app, images.get_image_at(app, _index))

def show_popup(message: str, icon_type: str, buttons: list, title: Optional[str]=None) -> str:
    """Display a popup dialog with a message, icon, and buttons.

    This function creates and displays a popup dialog with the specified message, icon, and buttons.
    It returns the text of the button that was clicked by the user.

    Args:
        message (str): The message to display in the popup.
        icon_type (str): The type of the icon to display in the popup.
        buttons (list): The list of button types to display in the popup.

    Returns:
        str: The text of the button that was clicked by the user.
    """
    popup = QMessageBox()

    # Set the icon
    icon = get_icon(icon_type)
    popup.setIcon(icon)

    # Set the window title, message, and buttons
    if title:
        popup.setWindowTitle(title)
    else:
        popup.setWindowTitle(icon_type)
    popup.setText(message)
    popup.setStandardButtons(get_buttons(buttons))
    popup.exec()

    # Show the popup and return the text of the clicked button
    return popup.clickedButton().text()

def get_icon(icon_type: str) -> QMessageBox.Icon:
    """Get the icon corresponding to the specified icon type.

    This function returns the icon object corresponding to the specified icon type.

    Args:
        icon_type (str): The type of the icon.

    Returns:
        QMessageBox.Icon: The icon object corresponding to the specified icon type.
    """
    icon_mapping = {
        "WARNING": QMessageBox.Icon.Warning,
        "QUESTION": QMessageBox.Icon.Question,
        "ERROR": QMessageBox.Icon.Critical,
        "INFO": QMessageBox.Icon.Information
    }

    # Return the icon object for the specified icon type, or NoIcon if not found
    return icon_mapping.get(icon_type, QMessageBox.Icon.NoIcon)

def get_buttons(buttons: list) -> QMessageBox.StandardButton:
    """Get the standard buttons corresponding to the specified button types.

    This function returns the standard buttons object corresponding to the specified button types.

    Args:
        buttons (list): The list of button types.

    Returns:
        QMessageBox.StandardButton: The standard buttons object corresponding to the specified button types.
    """
    button_mapping = {
        "OK": QMessageBox.StandardButton.Ok,
        "CANCEL": QMessageBox.StandardButton.Cancel,
        "YES": QMessageBox.StandardButton.Yes,
        "NO": QMessageBox.StandardButton.No,
        "SAVE": QMessageBox.StandardButton.Save,
        "DISCARD": QMessageBox.StandardButton.Discard,
        "CLOSE": QMessageBox.StandardButton.Close,
        "RETRY": QMessageBox.StandardButton.Retry,
        "IGNORE": QMessageBox.StandardButton.Ignore
    }

    # Initialize the standard buttons with NoButton
    standard_buttons = QMessageBox.StandardButton(QMessageBox.StandardButton.NoButton)

    # Iterate over the button types and add them to the standard buttons object
    for button in buttons:
        standard_buttons |= button_mapping.get(button, QMessageBox.StandardButton.NoButton)

    return standard_buttons

def config_changes_restart(app: 'classes.MainWindow.MainWindow', key: str, value: str) -> None:
    """Handle configuration changes and restart the application if necessary.

    This function displays a warning popup to inform the user about potential unsaved changes. If the user chooses
    to continue without saving, it restores the previous configuration settings in the menu. Otherwise, it updates
    the configuration settings with the new values and restarts the application.

    Args:
        app (classes.MainWindow.MainWindow): The main application window.
        key (str): The configuration key.
        value (str): The new configuration value.

    Returns:
        None
    """
    # Show a warning popup to confirm whether to continue without saving
    response = show_popup("Any unsaved changes will be lost.\nDo you want to continue ?", "WARNING", ["YES", "NO"])

    if response == "&No":
        # Restore the previous configuration settings in the menu
        for action in app.view_menu.actions():
            if action.menu():
                for action in action.menu().actions():
                    if action.text() == config.config_get(key):
                        action.setChecked(True)
        return

    # Update the configuration settings with the new values
    config.config_set(key, value)

    # Restart the application
    from main import restart
    restart()

def images_background(app: 'classes.main_window.MainWindow') -> None:
    """Set the background color for the application's views.

    Args:
        - app: The instance of MainWindow class.
    """

    # Prompt the user to select a color
    color = QColorDialog.getColor()

    if color.isValid():
        # Set the background color for the zoom view
        app.zoom_view.setStyleSheet(f"background-color: {color.name()}; border: 1px solid red;")

        # Set the background color for the main view
        app.main_view.setStyleSheet(f"QGraphicsView {{ background-color: {color.name()}; border: 1px solid red; }}")

        # Save the selected color in the configuration
        config.config_set("Background-color", color.name())

def about() -> None:
    show_popup('''RPG Maker - Set Manager
Version : 1.1.0
Author  : Costantin Hereiti
License : LGPL v3
Python  : 3.11.3 - 64Bit
PySide  : 6.5.1
''', "INFO", ["OK"], "About")

def report_issue() -> None:
    test = widgets.Form()
    if test.exec() == QDialog.Accepted:
        _title = test.title.text()
        _desc = test.desc.toPlainText()

        try:
            # Github Token won't be shared in source code
            # Github repo won't be shared in source code
            g = Github({Github_Token})
            _repo = g.get_repo({Github_repo})
            issue = _repo.create_issue(title=_title, body=_desc, labels=["issue"])
        except:
            print("This message is here because the github access token wasn't shared in the source code.")
            print("You can add your own github repository or remove any references to this function.")
            print("File: utils.py | line 321 | report_issue()")