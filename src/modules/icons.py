#================================================================================#
# File: icons.py
# Created Date: 05-06-2023 | 19:00:07
# Author: Hereiti
#================================================================================
# Last Modified: 08-06-2023 | 12:12:07
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
from typing import List, Optional, Tuple

#================================================================================#
# Third-party imports
#================================================================================#
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem

#================================================================================#
# Local imports
#================================================================================#
from modules import edits
from modules import images
from modules import maths
from modules import utils

#================================================================================#
# Functions
#================================================================================#
def add(app: 'classes.main_window.MainWindow', _image: QImage, _index: Tuple[int, int], history: bool=True) -> None:
    """
    Add an image to the specified cell in the main_view scene.

    Args:
        - app: The instance of the main_window
        - image: The QImage to be added
        - index: The index of the cell
    """
    if app.thread_running:
        return

    # Convert QGraphicsPixmapItem to QImage
    if isinstance(_image, QGraphicsPixmapItem):
        _image = _image.pixmap().toImage()

    # Check if the image has valid pixels
    if not images.has_pixel(_image):
        return

    # Remove any existing image at the cell index and store the temporary path
    _temp_path = remove(app, _index)

    # Get cell size from the app
    _cell_size = app.cell_size

    # Scale down the image if its dimensions exceed the cell size
    if _image.width() > _cell_size:
        _image = _image.scaled(_cell_size, _image.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    if _image.height() > _cell_size:
        _image = _image.scaled(_image.width(), _cell_size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)

    # Create a pixmap and draw the image onto it
    _pixmap = QPixmap(_cell_size, _cell_size)
    _pixmap.fill(Qt.GlobalColor.transparent)

    _painter = QPainter(_pixmap)
    _painter.drawImage(0, 0, _image)
    _painter.end()

    # Create a pixmap item and add it to the scene at the specified cell index
    _pixmap_item = QGraphicsPixmapItem(_pixmap)
    _pixmap_item.setPos(*maths.origin(_index))
    app.main_view.scene.addItem(_pixmap_item)

    # Update the images dictionary with the new pixmap item at the cell index
    app.images[_index] = _pixmap_item
    images.zoom(app, _pixmap_item)

    # Add the action to the undo history
    if history:
        edits.history(app, "ADD", _index, _temp_path)

def remove(app: 'classes.main_window.MainWindow', _index: Tuple[int, int], _history: bool = False) -> Optional[str]:
    """
    Remove the image at the specified cell index from the application.

    Args:
        app: The instance of the MainWindow class.
        index: The index of the cell.
        history: Whether to add the action to the history.

    Returns:
        The temporary path of the removed image, if available.
    """
    if app.thread_running:
        return

    # Initialize the temporary path
    _temp_path = None

    # Check if there is an image at the cell index
    if _index in app.images:
        _item = app.images[_index]
        app.main_view.scene.removeItem(_item)
        _temp_path = images.create_temp(app, _item)
        del app.images[_index]

    # Add the action to action history if specified
    if _history:
        edits.history(app, "DELETE", _index, _temp_path)

    # Update the zoom scene
    images.zoom(app, None)

    return _temp_path

def remove_images(app: 'classes.main_window.MainWindow'):
    """
    Remove any images contains in the main scene

    Args:
        - app: The instance of the MainWindow class
    """
    if app.thread_running:
        return

    # Remove all images from the main view
    for item in app.main_view.scene.items():
        if not isinstance(item, QGraphicsPixmapItem):
            continue
        app.main_view.scene.removeItem(item)
    app.images.clear()

def new(app: 'classes.main_window.MainWindow') -> None:
    """
    Create a new project by resetting the application and clearing history

    Args:
        - app: The instance of the MainWindow class
    """
    if app.thread_running:
        return

    # Show a warning popup to confirm new project creation
    response = utils.show_popup("Any unsaved changes will be lost.\nDo you want to continue without saving ?", "WARNING", ["YES", "NO"])

    if response != "&Yes":
        return

    remove_images(app)

    if app.main_view.highlight_selected[0]:
        app.main_view.scene.removeItem(app.main_view.highlight_selected[0])
        app.main_view.highlight_selected = [None, None]

    app.undo.clear()
    app.redo.clear()

def load(app: 'classes.main_window.MainWindow', image: Optional[QImage]=None,
    history: bool=False, reset: bool=False, index: Tuple[int, int]=(0, 0)) -> None:
    """
    Open an image in the application by creating pixmap items from the image and adding them to the scene.

    Args:
        - app: The instance of the MainWindow class.
        - image: The QImage to open in the application. If None, a file dialog will be shown to select an image.
        - history: A flag indicating whether to create a history entry for the open operation.
        - reset: Should the scene be reset before loading the new image
        - index: Where should the loop starts
    """
    if app.thread_running:
        return

    _cell_size = app.cell_size

    if not image:
        # Prompt for a png file
        image = utils.prompt_file(app)

    if not image:
        return

    if history and app.images:
        # Create an history entry
        _temp_path = images.create_temp_all(app)
        edits.history(app, "OVERHAUL", None, _temp_path)

    if reset:
        remove_images(app)

    _max_value = maths.grid_col() * max(min(image.height() // _cell_size, maths.grid_row()), 1)
    app.progress_bar.move(app.width() // 2 - app.progress_bar.width() // 2, app.height() // 2 - app.progress_bar.height() // 2)
    app.progress_bar.setVisible(True)
    _current_value = 0

    for column in range(maths.grid_col()):
        for row in range(max(min(image.height() // _cell_size + 1, maths.grid_row()), 1)):
            # Calculate the orgine of the cell
            _cell_origin = maths.origin((column, row))
            # Crop the image to the cell size
            crop_image =  image.copy(*_cell_origin, _cell_size, _cell_size)

            # Displays loop progression inside of a Progress Bar
            _current_value += 1
            progress = _current_value / _max_value * 100
            app.progress_bar.setValue(progress)

            if progress >= 100:
                app.progress_bar.setVisible(False)
                app.progress_bar.setValue(0)
                app.progress_bar.move(app.width(), app.height())

            # Skip empty image
            if not images.has_pixel(crop_image):
                continue

            # Calculate the origin based on passed index if it exists
            _cell_index = (column, row)
            if index:
                _cell_index = (column + index[0], row + index[1])
            _cell_origin = maths.origin(_cell_index)

            # Check if the click is out of bounds
            _limit = maths.origin((maths.grid_col() - 1, maths.grid_row() - 1))
            if any(_coord < 0 or _coord > limit for _coord, limit, in zip(_cell_origin, _limit)):
                continue

            # Create a pixmap with transparent background
            _pixmap = QPixmap(_cell_size, _cell_size)
            _pixmap.fill(Qt.GlobalColor.transparent)

            # Create a painter to draw image onto the pixmap
            _painter = QPainter(_pixmap)
            _painter.drawImage(0, 0, crop_image)
            _painter.end()

            if _cell_index in app.images:
                app.main_view.scene.removeItem(app.images[_cell_index])
                del app.images[_cell_index]

            # Create a pixmap item and set its position
            _pixmap_item = QGraphicsPixmapItem(_pixmap)
            _pixmap_item.setPos(*_cell_origin)

            # Adds it to app main scene and dict
            app.main_view.scene.addItem(_pixmap_item)
            app.images[_cell_index] = _pixmap_item

def add_after(app: 'classes.main_window.MainWindow') -> None:
    if app.thread_running:
        return

    _index = (0, maths.max_row(app) + 1)
    load(app=app, history=True, index=_index)

def folder(app: 'classes.main_window.MainWindow') -> None:
    """
    Add images from a selected folder to the grid

    Args:
        - app: The instance of the MainWindow class.
    """
    if app.thread_running:
        return

    _dir, _images = utils.prompt_folder(app)
    if len(_images) <= 0:
        return

    _cell_size = app.cell_size

    # Create a temp if there are already images loaded
    if app.images:
        _temp_path = images.create_temp_all(app)
        edits.history(app, "OVERHAUL", None, _temp_path)

    _col, _row = 1, maths.max_row(app) + 1
    _grid_col = maths.grid_col()
    _grid_row = maths.grid_row() + 1

    app.progress_bar.move(app.width() // 2 - app.progress_bar.width() // 2, app.height() // 2 - app.progress_bar.height() // 2)
    app.progress_bar.setVisible(True)

    for _index, _filename in enumerate(_images):
        _image_path = _dir.absoluteFilePath(_filename)

        # Move to the next row if the current column is the last
        if (_index + 1) % _grid_col == 0:
            _row += 1
            _col = 0

        # If the next rows exceed the max row count, stop adding image
        if _row > _grid_row:
            app.progress_bar.setValue(0)
            app.progress_bar.setVisible(False)
            app.progress_bar.move(app.width(), app.height())
            break

        # Calculate the origin from the index
        _cell_origin = maths.origin((_col, _row))

        # Convert the image at given path to sRGB and load it as QImage
        _image = QImage(_image_path)

        # Displays loop progression inside of a Progress Bar
        progress = (_index + 1) / len(_images) * 100
        app.progress_bar.setValue(progress)

        if progress >= 100:
            app.progress_bar.setValue(0)
            app.progress_bar.setVisible(False)
            app.progress_bar.move(app.width(), app.height())

        # Skip if no visible pixels
        if not images.has_pixel(_image):
            return

        # Scale the image if it exceed the cell size
        if _image.width() > _cell_size:
            _image = _image.scaled(_cell_size, _image.height())
        if _image.height() > _cell_size:
            _image = _image.scaled(_image.width(), _cell_size)

        # Create a pixmap with transparent pixels
        _pixmap = QPixmap(_cell_size, _cell_size)
        _pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter to draw the image onto the pixmap
        _painter = QPainter(_pixmap)
        _painter.drawImage(0, 0, _image)
        _painter.end()

        # Create a pixmap item with the pixmap and set its position
        _pixmap_item = QGraphicsPixmapItem(_pixmap)
        _pixmap_item.setPos(*_cell_origin)

        # Add the pixmap item to the main scene and dict
        app.main_view.scene.addItem(_pixmap_item)
        app.images[(_col, _row)] = _pixmap_item

        # Increase for the next iteration
        _col += 1
