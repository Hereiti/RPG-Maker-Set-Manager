#================================================================================#
# File: edits.py
# Created Date: 06-06-2023 | 10:49:05
# Author: Hereiti
#================================================================================
# Last Modified: 07-06-2023 | 16:40:55
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
from typing import List, Optional, Tuple, Union

#================================================================================#
# Third-party imports
#================================================================================#
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QGraphicsPixmapItem, QDialog, QInputDialog

#================================================================================#
# Local imports
#================================================================================#
from classes.widgets import TwoInputDialog

from modules import edits
from modules import icons
from modules import images
from modules import maths
from modules import utils

#================================================================================#
# Functions
#================================================================================#
def history(app: 'classes.main_window.MainWindow', action_type: str, index: Optional[Union[Tuple[int, int], List[Tuple[int, int]]]], temp: Optional[str], move_type: Optional[str] = None) -> None:
    """
    Update the history of actions performed in the application.

    Args:
        app (main_window.MainWindow): The instance of the main application window.
        action_type (str): The type of action performed.
        index (Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]): The index or indices associated with the action.
        temp (Optional[str]): The temporary data associated with the action.
        move_type (Optional[str], optional): The type of movement action. Defaults to None.
    """
    # Append the new action to the undo list and clear the redo list
    app.undo.append((action_type, index, temp, move_type))
    app.redo.clear()

def undo(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Undo the last action in application history

    Args:
        - app (main_window.MainWindow): The instance of the main application.
    """
    # Retrieve app attributes
    _undo = app.undo
    _redo = app.redo
    _images = app.images
    _main_view = app.main_view

    # Check if there is any action
    if not _undo:
        return

    # Retrieve the last action from the undo list
    _last_action = _undo.pop()
    _type, _index, _temp = _last_action[:3]

    if _type == "ADD":
        # Calculate the cell origin based on the index
        _cell_origin = maths.origin(_index)

        # Check if there is an item at the current index and removes it
        _item = _images[_index]
        _temp_path = None
        if _item:
            _temp_path = icons.remove(app, _index)

        # Check if there was an image before the image and re adds it
        if _temp:
            _pixmap_item = QGraphicsPixmapItem(QPixmap(_temp))
            _main_view.scene.addItem(_pixmap_item)
            _pixmap_item.setPos(*_cell_origin)
            _images[_index] = _pixmap_item

        # Append this action into the redo list
        _redo.append(("ADD", _index, _temp_path, None))

        # Create and add a highlight to the scene
        utils.highlight_index(app, _index)

    elif _type == "DELETE":
        # Calculate the cell origin based on the index
        _cell_origin = maths.origin(_index)

        # Check if there was an image before the image and re adds it
        icons.add(app, QImage(_temp), _index, False)

        # Append this action into the redo list
        _redo.append(("DELETE", _index, _temp_path, None))

        # Create and add a highlight to the scene
        utils.highlight_index(app, _index)

    elif _type == "MOVE":
        # Retrieve both indexes from the action argument
        _index_a, _index_b = _index

        # Retrieve the move type of the last action
        _move_type = _last_action[3]

        if _move_type == "SWITCH":
            # Retrieve the pixmap items corresponding to the cell indexes
            _item_a = _images.get(_index_a)
            _item_b = _images.get(_index_b)

            # Calculate cells origines based on the indexes
            _origin_a = maths.origin(_index_a)
            _origin_b = maths.origin(_index_b)

            if _item_a:
                _item_a.setPos(*_origin_b)
                _images[_index_b] = _item_a

            if _item_b:
                _item_b.setPos(*_origin_a)
                _images[_index_a] = _item_b

        elif _move_type == "OVERWRITE":
            # Retrieve the pixmap item corresponding to _index_b
            _images[_index_a] = _images[_index_b]
            del _images[_index_b]
            _item = _images[_index_a]
            _item.setPos(*maths.origin(_index_a))

            if _temp:
                icons.add(app, QImage(_temp), _index_b, False)

        # Add the action to the redo list
        _redo.append(("MOVE", _index, None, _move_type))

        # Create and add a highlight to the scene
        utils.highlight_index(app, _index_a)

    elif _type == "OVERHAUL":
        # Create a temp of the full populated view
        _temp_path = images.create_temp_all(app)

        if _temp:
            # Open the image and replace all icons
            icons.load(app=app, image=QImage(_temp), reset=True)
        else:
            # Remove all icons
            icons.reset(app)

        # Add the action to the redo list
        _redo.append(("OVERHAUL", None, _temp_path))

def redo(app: 'classes.main_window.MainWindow') -> None:
    """
    Redo the last undone action in the application

    Args:
        - app: The instance of the MainWindow class.
    """
    _undo = app.undo
    _redo = app.redo
    _images = app.images
    _main_view = app.main_view

    if not _redo:
        return

    # Retrieve the last action from the redo list
    _last_action = _redo.pop()
    _type, _index, _temp = _last_action[:3]

    if _type == "ADD":
        # Calculate the cell origin based on the cell index
        _cell_origin = maths.origin(_index)
        _temp_path = icons.remove(app, _index)

        # Create a pixmap with the temporary image to add back
        icons.add(app, QImage(_temp), _index, False)

        # Add the action back into the undo list
        _undo.append(("ADD", _index, _temp_path, None))

        # Create and add a highlight to the scene
        utils.highlight_index(app, _index)

    elif _type == "DELETE":
        # Remove the icon at the specified cell_index
        _temp_path = icons.remove(app, _index)

        # Add the action back to the undo list
        _undo.append(("DELETE", _index, _temp_path, None))

        # Create and add a highlight to the scene
        utils.highlight_index(app, _index)

    elif _type == "MOVE":
        # Retrieve indexes from last action index parameters
        _index_a, _index_b = _index
        _move_type = _last_action[3]

        # Initialize temp path
        _temp_path = 0

        if _move_type == "SWITCH":
            _item_a = _images[_index_a]
            _item_b = _images[_index_b]

            _origin_a = maths.origin(_index_a)
            _origin_b = maths.origin(_index_b)

            if _item_a:
                _item_a.setPos(*_origin_b)
                _images[_index_b] = _item_a

            if _item_b:
                _item_b.setPos(*_origin_a)
                _images[_index_a] = _item_b

            # Add the action back to the undo list
            _undo.append(("MOVE", _index, None, _move_type))

        elif _move_type == "OVERWRITE":
            # If the move_type is "OVERWRITE", remove the icon at index_1 and get the temporary path
            _temp_path = icons.remove(app, _index_b)

            _item = _images[_index_a]
            _item.setPos(*maths.origin(_index_b))
            _images[_index_b] = _item
            del _images[_index_a]

            # Add the action back to the undo list
            _undo.append(("MOVE", _index, _temp_path, _move_type))

        # Create and add a highlight to the scene
        utils.highlight_index(app, _index_b)

    elif _type == "OVERHAUL":
        # Create temporary files of the main view
        _temp_path = images.create_temp_all(app)

        # Open the previous image again
        if _temp:
            icons.load(app=app, image=QImage(_temp), reset=True)
        else:
            icons.remove_images(app)

        # Add the action back to the undo list
        _undo.append(("OVERHAUL", None, _temp_path, None))

def copy(app: 'classes.main_window.MainWindow') -> None:
    """
    Copy the selected icon in the application.

    Args:
        - app: The instance of the MainWindow class.
    """
    # Check if there is a selected cell
    if app.main_view.highlight_selected:
        # Check if the cell index exists in the images dict
        _index = app.main_view.highlight_selected[1]
        if _index in app.images:
            # Store it inside of the app attribute
            app.copied_img = app.images[_index]

def cut(app: 'classes.main_window.MainWindow') -> None:
    """
    Copy then remove the image from the selected cell

    Args:
        - app: The instance of the MainWindow class
    """
    # Check if there is a selected cell
    if app.main_view.highlight_selected:
        # Check if the cell index exists in the images dict
        _index = app.main_view.highlight_selected[1]
        if _index in app.images:
            # Copy the selected icon then remove
            copy(app)
            icons.remove(app, _index, True)

def paste(app: 'classes.main_window.MainWindow') -> None:
    """
    Paste the copied image onto the selected cell.

    Args:
        - app: The instance of the MainWindow class.
    """
    # Check if there is a selected cell and a copied image
    if app.main_view.highlight_selected and app.copied_img:
        # Get the index and origin of the selected cell
        _index = app.main_view.highlight_selected[1]
        _origin = maths.origin(_index)

        # Add the copied image to the scene
        icons.add(app, app.copied_img, _index)

def offset(app: 'classes.main_window.MainWindow', direction: str=None, _x=None, _y=None) -> None:
    """
    Offset the icon in the selected cell of the application by one
    cell in the specified direction.

    Args:
        - app: The instance of the MainWindow class.
        - direction: The direction to offset the icon.
            Possible values: "RIGHT", "LEFT", "DOWN", "UP".
    """
    # Check if there is a selected cell
    if not app.main_view.highlight_selected[0]:
        return

    # Get the index of the selected cell
    _index = app.main_view.highlight_selected[1]

    # Check if the index exists in the icons dictionary
    if _index in app.images:
        # Get the pixmap of the selected cell
        _image_pixmap = app.images[_index].pixmap()

        # Create a new pixmap which will hold the offset image
        _offset_pixmap = QPixmap(app.cell_size, app.cell_size)
        _offset_pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter to draw the offset pixmap
        _painter = QPainter(_offset_pixmap)

        # Determine the offset values based on the specified direction
        offset_x = offset_y = 0
        if direction == "Right":
            offset_x, offset_y = 1, 0
        elif direction == "Left":
            offset_x, offset_y = -1, 0
        elif direction == "Down":
            offset_x, offset_y = 0, 1
        elif direction == "Up":
            offset_x, offset_y = 0, -1
        else:
            if _x:
                offset_x = _x
            if _y:
                offset_y = _y

        # Draw the offset pixmap by applying the offset values
        _painter.drawPixmap(offset_x, offset_y, _image_pixmap)
        _painter.end()

        # Create a new pixmap item with the offset pixmap
        _pixmap_item = QGraphicsPixmapItem(_offset_pixmap)
        icons.add(app, _pixmap_item, _index)

def change_hue(app: 'classes.main_window.MainWindow') -> None:
    if not app.main_view.highlight_selected[0]:
        return

    value, ok = QInputDialog.getText(None, "Image Hue", "Enter the new hue value (0-359):", text=str(app.last_hue))

    if not ok:
        return

    if value.isdigit():
        value = int(value)
        if value > 359 or value < 0:
            return

        hue_slider = app.sliders["Hue"]
        hue_slider.change_hue(app, value)
        hue_slider.on_slider_end(app)

def change_saturation(app: 'classes.main_window.MainWindow') -> None:
    if not app.main_view.highlight_selected[0]:
        return

    value, ok = QInputDialog.getText(None, "Image Saturation", "Enter the new saturation value (0-255):", text=str(app.last_saturation))

    if not ok:
        return

    if value.isdigit():
        value = int(value)
        if value > 255 or value < 0:
            return

        saturation_slider = app.sliders["Saturation"]
        saturation_slider.change_saturation(app, value)
        saturation_slider.on_slider_end(app)

def change_brightness(app: 'classes.main_window.MainWindow') -> None:
    if not app.main_view.highlight_selected[0]:
        return

    value, ok = QInputDialog.getText(None, "Image Saturation", "Enter the new saturation value (-255-255):", text=str(app.last_brightness))

    if not ok:
        return

    if value.isdigit() or value.startswith("-") and value[1:].isdigit():
        value = int(value)
        if value > 255 or value < -255:
            return

        brightness_slider = app.sliders["Brightness"]
        brightness_slider.change_brightness(app, value)
        brightness_slider.on_slider_end(app)

def change_offset(app: 'classes.main_window.MainWindow') -> None:
    if not app.main_view.highlight_selected[0]:
        return

    cell_size = app.cell_size
    dialog = TwoInputDialog(title="Offset", text_1=f"Offset X (-{cell_size}:{cell_size}):", value_1="0", text_2=f"Offset Y (-{cell_size}:{cell_size}):", value_2="0")
    if dialog.exec() == QDialog.Accepted:
        # Retrieve the values from the text boxes
        offset_x = dialog.textbox1.text()
        offset_y = dialog.textbox2.text()

        if (offset_x.startswith("-") and offset_x[1:].isdigit() or offset_x.isdigit()) and (offset_y.startswith("-") and offset_y[1:].isdigit() or offset_y.isdigit()):
            offset_x = int(offset_x)
            offset_y = int(offset_y)
        else:
            return

        offset(app=app, _x=offset_x, _y=offset_y)
    else:
        return

def flip_image(app: 'classes.main_window.MainWindow', orientation=None) -> None:
    # Check if there is a selected cell
    if not app.main_view.highlight_selected[0]:
        return

    # Get the index of the selected cell
    _index = app.main_view.highlight_selected[1]

    # Check if the index exists in the icons dictionary
    if _index in app.images:
        # Get the pixmap of the selected cell
        _image = app.images[_index].pixmap().toImage()

        _transform = QTransform()
        if orientation == "Vertical":
            _transform.scale(-1, 1)
        elif orientation == "Horizontal":
            _transform.scale(1, -1)
        else:
            return

        _flipped_image = _image.transformed(_transform)
        icons.add(app, _flipped_image, _index)

def change_color(app: 'classes.main_window.MainWindow', color=None) -> None:
    if not color:
        return
    if not app.main_view.highlight_selected[0]:
        return

    value, ok = QInputDialog.getText(None, "Specific Color", f"Enter the value for the {color} color (-255-255):", text=str(app.last_color[color]))

    if not ok:
        return

    if value.isdigit() or value.startswith("-") and value[1:].isdigit():
        value = int(value)
        if value > 255 or value < -255:
            return

        if color == "red":
            red_slider = app.sliders["R"]
            red_slider.change_color(app, value, "red")
            red_slider.on_slider_end(app)
        elif color == "green":
            green_slider = app.sliders["G"]
            green_slider.change_color(app, value, "green")
            green_slider.on_slider_end(app)
        elif color == "blue":
            blue_slider = app.sliders["B"]
            blue_slider.change_color(app, value, "blue")
            blue_slider.on_slider_end(app)
