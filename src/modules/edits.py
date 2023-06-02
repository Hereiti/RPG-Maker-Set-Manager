#================================================================================#
# File: edits.py
# Created Date: 26-05-2023 | 17:39:44
# Author: Hereiti
#================================================================================
# Last Modified: 02-06-2023 | 11:24:56
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Import
#================================================================================#
from typing import Optional, Tuple, Union, List

#================================================================================#
# Third-Party Import
#================================================================================#
from PySide6.QtCore    import Qt
from PySide6.QtGui     import QPixmap, QImage, QPainter, QTransform
from PySide6.QtWidgets import QGraphicsPixmapItem

#================================================================================#
# Local Application Import
#================================================================================#
from modules import maths, images, icons, edits, utils

#================================================================================#
# Functions
#================================================================================#
def history(app: 'classes.MainWindow.MainWindow', action_type: str, index: Optional[Union[Tuple[int, int], List[Tuple[int, int]]]], temp: Optional[str], move_type: Optional[str] = None) -> None:
    """
    Update the history of actions performed in the application.

    Args:
        app (MainWindow.MainWindow): The instance of the main application window.
        action_type (str): The type of action performed.
        index (Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]): The index or indices associated with the action.
        temp (Optional[str]): The temporary data associated with the action.
        move_type (Optional[str], optional): The type of movement action. Defaults to None.

    Returns:
        None
    """
    # Append the new action to the undo list
    app.undo.append((action_type, index, temp, move_type))

    # Clear the redo list
    app.redo = []

def undo(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Undo the last action in the application.

    Args:
        app (MainWindow.MainWindow): The instance of the main application window.

    Returns:
        None
    """

    # Retrieve the undo, redo, and icons lists from the application
    _undo, _redo, _icons = app.undo, app.redo, app.icons

    # Check if there are any actions to undo
    if not _undo:
        return

    # Retrieve the last action from the undo list
    last_action = _undo.pop()
    _type, cell_index, _temp = last_action[:3]

    if _type == "ADD":
        # Create and add a highlight item to the scene
        utils.highlight_selected(app, cell_index)

        # Calculate the cell origin based on the cell index
        cell_origin = maths.origin(*cell_index)

        _item: Optional[QGraphicsPixmapItem] = _icons[cell_index]
        if _item is not None:
            # Create a temporary file for the item and remove it from the scene
            temp_path = images.create_temp(app, _item)
            app.main_view.scene.removeItem(_item)
            del _icons[cell_index]

        if _temp is not None:
            # Create a new pixmap item with the temporary image and add it to the scene
            pixmap_item = QGraphicsPixmapItem(QPixmap(_temp))
            pixmap_item.setPos(*cell_origin)
            app.main_view.scene.addItem(pixmap_item)
            _icons[cell_index] = pixmap_item

        # Append the reverse action to the redo list
        _redo.append(("ADD", cell_index, temp_path, None))

    elif _type == "DELETE":
        # Create and add a highlight item to the scene
        utils.highlight_selected(app, cell_index)

        # Calculate the cell origin based on the cell index
        cell_origin = maths.origin(*cell_index)

        # Create a new pixmap item with the temporary image and add it to the scene
        pixmap_item = QGraphicsPixmapItem(QPixmap(_temp))
        pixmap_item.setPos(*cell_origin)
        app.main_view.scene.addItem(pixmap_item)
        _icons[cell_index] = pixmap_item

        # Append the reverse action to the redo list
        _redo.append(("DELETE", cell_index, None, None))

    elif _type == "MOVE":
        # Retrieve the cell indices from the index tuple
        index_0, index_1 = cell_index

        # Create and add a highlight item to the scene
        utils.highlight_selected(app, index_0)
        
        # Retrieve the move_type from the last_action
        move_type = last_action[3]

        if move_type == "SWITCH":
            # Retrieve the pixmap items corresponding to the cell indices
            item_0: Optional[QGraphicsPixmapItem] = _icons.get(index_0)
            item_1: Optional[QGraphicsPixmapItem] = _icons.get(index_1)

            # Calculate the cell origins based on the cell indices
            cell_origin_0: Tuple[int, int] = maths.origin(*index_0)
            cell_origin_1: Tuple[int, int] = maths.origin(*index_1)

            if item_0 is not None:
                # Move item_0 to the position of cell_1 and restore its opacity
                item_0.setPos(*cell_origin_1)
                item_0.setOpacity(1.0)

            if item_1 is not None:
                # Move item_1 to the position of cell_0
                item_1.setPos(*cell_origin_0)

            # Update the pixmap items in the icons dictionary
            _icons[index_0] = item_1
            _icons[index_1] = item_0

        elif move_type == "OVERWRITE":
            # Retrieve the pixmap item corresponding to index_1
            item: Optional[QGraphicsPixmapItem] = _icons[index_1]
            if item is not None:
                # Move the item to the position of index_0
                item.setPos(*maths.origin(*index_0))
                _icons[index_0] = item

            if _temp:
                # Create a new pixmap item with the temporary image and add it to the scene
                pixmap_item = QGraphicsPixmapItem(QPixmap(_temp))
                pixmap_item.setPos(*maths.origin(*index_1))
                app.main_view.scene.addItem(pixmap_item)
                _icons[index_1] = pixmap_item
            else:
                del _icons[index_1]

        _redo.append(("MOVE", cell_index, None, move_type))

    elif _type == "OVERHAUL":
        # Create temporary files for all icons in the application
        temp_path = images.create_temp_all(app)

        if _temp:
            # If _temp is not None, open the image and replace all icons
            icons.load(app, QImage(_temp), False)
        else:
            # If _temp is None, reset the main_view.scene by removing all items
            icons.reset(app.main_view.scene)

        # Add the action to redo list with the necessary information
        _redo.append(("OVERHAUL", None, temp_path))

    if app.main_view.highlight_selected is not None:
        images.zoom(app, images.image_at(app, app.main_view.highlight_selected[1]))

def redo(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Redo the last undone action in the application.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    _undo, _redo, _icons = app.undo, app.redo, app.icons

    if not _redo:
        return

    # Retrieve the last action from the undo list
    last_action = _redo.pop()
    _type, cell_index, _temp = last_action[:3]

    if _type == "ADD":
        # Create and add a highlight item to the scene
        utils.highlight_selected(app, cell_index)

        # Calculate the cell origin based on the cell index
        cell_origin = maths.origin(*cell_index)
        temp_path = icons.remove(app, cell_index)

        # Create a new pixmap item with the temporary image and add it to the scene
        pixmap_item = QGraphicsPixmapItem(QPixmap(_temp))
        pixmap_item.setPos(*cell_origin)
        app.main_view.scene.addItem(pixmap_item)
        _icons[cell_index] = pixmap_item

        # Add the action to undo list with the necessary information
        _undo.append(("ADD", cell_index, temp_path, None))

    elif _type == "DELETE":
        # Create and add a highlight item to the scene
        utils.highlight_selected(app, cell_index)

        # Remove the icon at the specified cell_index and get the temporary path
        temp_path = icons.remove(app, cell_index)

        # Add the action to the undo list with the necessary information
        _undo.append(("DELETE", cell_index, temp_path, None))

    elif _type == "MOVE":
        # Retrieve the two cell indices involved in the move operation
        index_0, index_1 = cell_index
        
        # Create and add a highlight item to the scene
        utils.highlight_selected(app, index_1)

        # Retrieve the move_type from the last_action
        move_type = last_action[3]

        # Initialize temp_path to None
        temp_path = None

        if move_type == "SWITCH":
            # If the move_type is "SWITCH", swap the positions of the two items
            item_0: Optional[QGraphicsPixmapItem] = _icons[index_0]
            item_1: Optional[QGraphicsPixmapItem] = _icons[index_1]

            cell_origin_0: Tuple[int, int] = maths.origin(*index_0)
            cell_origin_1: Tuple[int, int] = maths.origin(*index_1)

            if item_0 is not None:
                item_0.setPos(*cell_origin_1)

            if item_1 is not None:
                item_1.setPos(*cell_origin_0)

            _icons[index_0] = item_1
            _icons[index_1] = item_0

        elif move_type == "OVERWRITE":
            # If the move_type is "OVERWRITE", remove the icon at index_1 and get the temporary path
            temp_path = icons.remove(app, index_1)

            _item: Optional[QGraphicsPixmapItem] = _icons[index_0]
            if _item is not None:
                _item.setPos(*maths.origin(*index_1))
                _icons[index_1] = _item
                del _icons[index_0]

        # Add the action to the undo list with the necessary information
        _undo.append(("MOVE", cell_index, temp_path, move_type))

    elif _type == "OVERHAUL":
        # Create temporary files for all icons in the application
        temp_path = images.create_temp_all(app)

        if _temp:
            # If _temp is not None, open the image and replace all icons
            icons.load(app, QImage(_temp), False)
        else:
            # If _temp is None, reset the main_view.scene by removing all items
            icons.reset(app.main_view.scene)

        # Add the action to the undo list with the necessary information
        _undo.append(("OVERHAUL", None, temp_path))

    if app.main_view.highlight_selected is not None:
        images.zoom(app, images.image_at(app, app.main_view.highlight_selected[1]))

def copy(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Copy the selected icon in the application.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    # Check if there is a selected icon
    if app.main_view.highlight_selected is not None:
        cell_index = app.main_view.highlight_selected[1]
        # Check if the selected icon exists in the icons dictionary
        if cell_index in app.icons:
            # Store the selected icon in the copied_icon variable
            app.copied_icon = app.icons[cell_index]

def cut(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Cut the selected icon in the application by copying it and removing it from the scene.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    # Check if there is a selected icon
    if app.main_view.highlight_selected:
        # Copy the selected icon
        copy(app)
        # Remove the selected icon from the scene
        icons.remove(app, app.main_view.highlight_selected[1], True)

def paste(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Paste the copied icon onto the selected cell in the application.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    # Check if there is a selected cell and a copied icon
    if app.main_view.highlight_selected and app.copied_icon:
        # Get the index and origin of the selected cell
        cell_index = app.main_view.highlight_selected[1]
        cell_origin = maths.origin(*cell_index)

        # Create a temporary image from the selected cell
        temp_path = images.create_temp(app, images.image_at(app, cell_index))
        icons.remove(app, cell_index)

        # Create a new pixmap item with the copied icon and add it to the scene
        copied_item = QGraphicsPixmapItem()
        copied_item.setPixmap(app.copied_icon.pixmap())
        copied_item.setPos(*cell_origin)
        app.main_view.scene.addItem(copied_item)
        app.icons[cell_index] = copied_item

        # Add the paste action to the undo history
        edits.history(app, "ADD", cell_index, temp_path)

def offset(app: 'classes.MainWindow.MainWindow', direction: str) -> None:
    """
    Offset the icon in the selected cell of the application by one cell in the specified direction.

    Args:
        app: The instance of the MainWindow class.
        direction: The direction to offset the icon. Possible values: "RIGHT", "LEFT", "DOWN", "UP".

    Returns:
        None.
    """
    # Check if there is a selected cell
    if not app.main_view.highlight_selected:
        return

    # Get the index of the selected cell
    cell_index = app.main_view.highlight_selected[1]

    # Check if the cell index exists in the icons dictionary
    if cell_index in app.icons:
        # Get the pixmap of the icon in the selected cell
        icon_pixmap = app.icons[cell_index].pixmap()

        # Create a new pixmap with the size of a cell
        offset_pixmap = QPixmap(maths.cell_size(), maths.cell_size())
        offset_pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter to draw the offset pixmap
        painter = QPainter(offset_pixmap)

        # Determine the offset values based on the specified direction
        if direction == "Right":
            offset_x, offset_y = 1, 0
        elif direction == "Left":
            offset_x, offset_y = -1, 0
        elif direction == "Down":
            offset_x, offset_y = 0, 1
        elif direction == "Up":
            offset_x, offset_y = 0, -1
        else:
            return

        # Draw the offset pixmap by applying the offset values to the icon pixmap
        painter.drawPixmap(offset_x, offset_y, icon_pixmap)
        painter.end()

        # Create a new pixmap item with the offset pixmap and add it to the icons dictionary
        pixmap_item = QGraphicsPixmapItem(offset_pixmap)
        icons.add(app, pixmap_item, cell_index)
        images.zoom(app, pixmap_item)

def rotate_image(app: 'classes.MainWindow.MainWindow', value: int) -> None:
    """
    Rotate the image in the selected cell of the application by the specified value in degrees.

    Args:
        app: The instance of the MainWindow class.
        value: The rotation value in degrees.

    Returns:
        None.
    """
    # Check if there is a selected cell
    if not app.main_view.highlight_selected:
        return

    # Get the index and size of the selected cell
    cell_index = app.main_view.highlight_selected[1]
    cell_size = maths.cell_size()

    # Get the image in the selected cell
    icon = images.image_at(app, cell_index)
    if icon:
        # Update the rotation value displayed on the button
        app.buttons["Rotate"].setText(f"{value}°")

        # Set the transform origin and rotation of the icon pixmap
        icon.setTransformOriginPoint(cell_size // 2, cell_size // 2)
        icon.setRotation(value)

        # Get the pixmap of the image
        icon_pixmap = icon.pixmap()

        # Create a new pixmap with the rotated image
        rotate_pixmap = QPixmap(cell_size, cell_size)
        rotate_pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter to draw the rotated pixmap
        painter = QPainter(rotate_pixmap)
        painter.translate(cell_size // 2, cell_size // 2)
        painter.rotate(icon.rotation())
        painter.drawPixmap(-cell_size // 2, -cell_size // 2, icon_pixmap)
        painter.end()

        # Store the modified icon as a QGraphicsPixmapItem
        app.modified_icon = QGraphicsPixmapItem(rotate_pixmap)
        images.zoom(app, app.modified_icon)

def resize_image(app: 'classes.MainWindow.MainWindow', value: int) -> None:
    """
    Resize the image in the selected cell of the application by the specified value.

    Args:
        app: The instance of the MainWindow class.
        value: The resizing value in percentage.

    Returns:
        None.
    """
    # Check if there is a selected cell
    if not app.main_view.highlight_selected:
        return

    # Get the index and size of the selected cell
    cell_index = app.main_view.highlight_selected[1]
    cell_size = maths.cell_size()

    # Get the pixmap of the image in the selected cell
    icon_pixmap = images.image_at(app, cell_index).pixmap()
    if icon_pixmap:
        # Create a new pixmap with the resized image
        resize_pixmap = QPixmap(cell_size, cell_size)
        resize_pixmap.fill(Qt.GlobalColor.transparent)

        # Calculate the new width and height based on the resizing value
        new_width = icon_pixmap.width() * value / 100
        new_height = icon_pixmap.height() * value / 100

        # Calculate the offsets to center the resized image
        _dx = (cell_size - new_width) // 2
        _dy = (cell_size - new_height) // 2

        # Create a transform to apply the resizing and centering
        transform = QTransform()
        transform.translate(_dx, _dy)
        transform.scale(value / 100, value / 100)
        transform.translate(-_dx, -_dy)
        icon_pixmap = icon_pixmap.transformed(transform)

        # Create a painter to draw the resized pixmap
        painter = QPainter(resize_pixmap)
        painter.drawPixmap(int(_dx), int(_dy), icon_pixmap)
        painter.end()

        # Store the modified icon as a QGraphicsPixmapItem
        app.labels["ResizeValue"].setText(f"{value}%")
        app.modified_icon = QGraphicsPixmapItem(resize_pixmap)
        images.zoom(app, app.modified_icon)

def on_slider_end(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Perform actions when the sliders are released.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    # Check if there is a selected cell
    if not app.main_view.highlight_selected:
        return

    # Get the index of the selected cell
    cell_index = app.main_view.highlight_selected[1]

    # Add the modified icon to the icons dictionary
    icons.add(app, app.modified_icon, cell_index)
    images.zoom(app, app.modified_icon)

    connect_slider = {"Rotate", "Resize"}
    for slider in connect_slider:
        app.sliders[slider].blockSignals(True)

        if slider == "Rotate":
            app.sliders[slider].setValue(0)
            app.buttons[slider].setText("0°")
        elif slider == "Resize":
            app.sliders[slider].setValue(100)

        app.sliders[slider].blockSignals(False)


    app.modified_icon = None
