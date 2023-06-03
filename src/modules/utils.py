#================================================================================#
# File: utils.py
# Created Date: 22-05-2023 | 13:22:52
# Author: Hereiti
#================================================================================
# Last Modified: 04-06-2023 | 00:46:33
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Imports
#================================================================================#
from typing import Tuple, Optional
import re
import sys

#================================================================================#
# Third-Party Imports
#================================================================================#
from PySide6.QtCore    import QPointF, QRectF
from PySide6.QtGui     import QMouseEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QMainWindow, QMessageBox, QColorDialog, QMenu

#================================================================================#
# Local Application Imports
#================================================================================#
from classes import GraphcisItem, MainWindow
from modules import config, maths, images, miscellaneous

#================================================================================#
# Functions
#================================================================================#
def click_cell(event: QMouseEvent, app: 'classes.MainWindow.MainWindow') -> None:
    """Handle the click event on a cell.

    This function is called when a cell is clicked in the main view.

    Args:
        event (QMouseEvent): The mouse event triggered by the click.
        app ('classes.MainWindow.MainWindow'): The main window application instance.

    Returns:
        None
    """
    main_view = app.main_view
    cell_size = maths.cell_size()

    # Map the event position to scene coordinates
    scene_pos = main_view.mapToScene(event.pos())
    _x, _y = scene_pos.x(), scene_pos.y()

    # Calculate the cell index and origin
    cell_index: Tuple[int, int] = maths.index(_x, _y)
    cell_origin: Tuple[int, int] = maths.origin(*cell_index)

    # Calculate the limit for cell origin coordinates
    limit: Tuple[int, int] = maths.origin(maths.grid_col() - 1, maths.grid_row() - 1)

    # Check if the cell origin is within the limits
    if any(coord < 0 or coord > limit for coord, limit in zip(cell_origin, limit)):
        return

    highlight_selected(app, cell_index)

    cell_rect = QRectF(*cell_origin, cell_size, cell_size)
    _item: Optional[QGraphicsPixmapItem] = None

    # Find the first pixmap item that collides with the highlight item
    for item in main_view.scene.items(cell_rect):
        if isinstance(item, QGraphicsPixmapItem) and item != main_view.highlight_selected[0]:
            if item.collidesWithItem(main_view.highlight_selected[0]):
                _item = item
                break

    num: int = cell_index[1] * 16 + cell_index[0] + 1
    app.labels["Index"].setText(f"● [{cell_index[0]}:{cell_index[1]}] - Icon n°{num} ●")
    images.zoom(app, _item)

    if _item:
        miscellaneous.connect_edits_widget(app, True)
    else:
        miscellaneous.connect_edits_widget(app)

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
        for menu in app.menu_bar.actions():
            menu_i = menu.menu()
            if isinstance(menu_i, QMenu):
                for action in menu_i.actions():
                    if action.text() == config.get_config(key):
                        action.setChecked(True)
        return

    # Update the configuration settings with the new values
    config.set_config(key, value)

    # Restart the application
    from main import restart
    restart()

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

def images_background(app: QMainWindow) -> None:
    """Set the background color for the application's views.

    Args:
        app (QMainWindow): The main application window.

    """
    if not isinstance(app, MainWindow.MainWindow):
        return

    # Prompt the user to select a color
    color = QColorDialog.getColor()

    if color.isValid():
        # Set the background color for the zoom view
        app.zoom_view.setStyleSheet(f"background-color: {color.name()}; border: 1px solid red;")

        # Set the background color for the main view
        app.main_view.setStyleSheet(f"QGraphicsView {{ background-color: {color.name()}; border: 1px solid red; }}")

        # Save the selected color in the configuration
        config.set_config("Background-color", color.name())

def highlight_selected(app: 'classes.MainWindow.MainWindow', cell_index) -> None:
    """Highlights the selected cell in the main view.

    Args:
        app (classes.MainWindow.MainWindow): The main window application instance.
        cell_index: The index of the selected cell.

    Returns:
        None

    This function creates a highlight item and adds it to the scene to visually
    highlight the selected cell. If there is an existing highlight item, it updates
    its position and index.

    """
    # Create and add a highlight item to the scene
    if not app.main_view.highlight_selected:
        app.main_view.highlight_selected = [GraphcisItem.Highlight(color="red"), cell_index]
        app.main_view.scene.addItem(app.main_view.highlight_selected[0])
        app.main_view.highlight_selected[0].setZValue(2.0)
        app.main_view.highlight_selected[0].setOpacity(0.7)

    # Set the position and index of the highlight item
    app.main_view.highlight_selected[0].setPos(QPointF(*maths.origin(*cell_index)))
    app.main_view.highlight_selected[1] = cell_index

def about() -> None:
    show_popup('''RPG Maker - Set Manager
Version : 1.0.5
Author  : Costantin Hereiti
License : LGPL v3
Python  : 3.11.3 - 64Bit
PySide  : 6.5.1
''', "INFO", ["OK"], "About")
