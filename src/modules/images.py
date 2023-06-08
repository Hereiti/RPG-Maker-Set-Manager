#================================================================================#
# File: images.py
# Created Date: 05-06-2023 | 18:39:10
# Author: Hereiti
#================================================================================
# Last Modified: 07-06-2023 | 20:40:40
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
import tempfile
import time
import os

from typing import Optional, Tuple
from functools import partial

#================================================================================#
# Third-party imports
#================================================================================#
from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QFileDialog, QInputDialog, QGraphicsPixmapItem

from PIL import Image, ImageQt, ImageCms

#================================================================================#
# Local imports
#================================================================================#
from modules import config
from modules import maths
from modules import utils

#================================================================================#
# Functions
#================================================================================#
def get_image_at(app: 'classes.main_window.MainWindow', index: Tuple[int, int]) -> Optional[QGraphicsPixmapItem]:
    """
    Get the QGraphicsPixmapItem at the specified index in the app
    images dictionnary.
    
    Args:
        - app: The instance of the MainWindow class
        - index: The index of the cell

    Returns:
        - Optinal[QGraphicsPixmapItem]: The QGraphicsPixmapItem at the
            specified index, or None if not found.
    """
    if index in app.images:
        # Return the QGraphicsPixmapItem at the specified index
        return app.images[index]

    # Return None if the index is not present
    return None

def zoom(app: 'classes.main_window.MainWindow', item: Optional[QGraphicsPixmapItem]) -> None:
    """
    Zoom in on the specified QGraphicsPixmapItem.

    Args:
        - app: The instance of the MainWindow class.
        - item: The QGraphicsPixmapItem to zoom in on.
    """
    app.zoom_scene.clear()
    if item is not None:
        # Define the desired width and height
        width = 160
        height = 160
        
        # Scale the pixmap to the desired width and height with the best quality
        pixmap = item.pixmap().scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        app.zoom_scene.addItem(QGraphicsPixmapItem(pixmap))

def has_pixel(image: QImage) -> bool:
    """
    Checks if the given image has any pixel with alpha higher than 25

    Args:
        - image: The image to check

    Returns:
        bool: True if the image has at least one pixel with an alpha
            higher than 25, False otherwise
    """
    # Convert the QImage to a PIL image
    _pil_image = Image.fromqpixmap(image)

    # Get the alpha channel of the image
    _alpha = _pil_image.split()[-1]

    # Check if there are any "visible" pixels (alpha >= 25)
    return any(pixel >= 25 for pixel in _alpha.getdata())

def create_temp(app: 'classes.main_window.MainWindow', image: Optional[QGraphicsPixmapItem]) -> Optional[str]:
    """
    Create a temporary file from the image

    Args:
        - image: The QGraphicsPixmapItem containing the image

    Returns:
        - str: The path of the temporary file
    """
    if not image:
        return None

    # Check that we are not creating a temp for a "empty" image
    if isinstance(image, QGraphicsPixmapItem):
        image = image.pixmap().toImage()
    if not has_pixel(image):
        return None

    # Create a temporary file with the .png extension
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        app.temp.append(temp.name)
        image.save(temp.name)
        return temp.name

def create_temp_all(app: 'classes.main_window.MainWindow') -> Optional[str]:
    """
    Create a temporary file containing all the images in the grid.

    Args:
        - app: The instance of the MainWindow class.

    Returns:
        - str: The path of the temporary file.
    """
    # Retrieve cell size attribute from the app
    _cell_size = app.cell_size

    # Check that we have item in the grid
    if app.images is None:
        return None

    # Calculate the width and height of the current state
    _width = maths.grid_col() * _cell_size
    _height = (maths.max_row(app) + 1) * _cell_size

    # Create a pixmap with those specifics size
    _pixmap = QPixmap(_width, _height)
    _pixmap.fill(Qt.GlobalColor.transparent)

    _painter = QPainter(_pixmap)
    _painter.drawPixmap(0, 0, _pixmap)

    # Iterate over every items in the scene and draw QGraphicsPixmap as pixmap
    for item in app.main_view.scene.items():
        if isinstance(item, QGraphicsPixmapItem):
            _pos = item.pos()
            _pixmap_item = item.pixmap()
            _item_pos = QPoint(_pos.x(), _pos.y())
            _painter.drawPixmap(_item_pos, _pixmap_item)

    _painter.end()

    # Create the temporary file with the .png extension
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        app.temp.append(temp.name)
        _pixmap.save(temp.name)
        return temp.name

def save_selected(app: 'classes.main_window.MainWindow') -> None:
    """
    Save the selected cell as an image file.

    Args:
        - app: The instance of the MainWindow class.
    """
    if not app.main_view.highlight_selected[0]:
        return

    _img = get_image_at(app, app.main_view.highlight_selected[1])
    if _img is None:
        return utils.show_popup("You cannot save an empty cell.", "INFO", ["OK"])

    # Get the file path to save the image
    file_path, _ = QFileDialog.getSaveFileName(None, "Save File", "", "PNG Files(*.png)")

    if file_path:
        # Save the pixmap as an image file
        _pixmap = _img.pixmap()
        _pixmap.save(file_path)

def save_separately(app: 'classes.main_window.MainWindow') -> None:
    """
    Save each icon in the grid as individual image files.

    Args:
        - app: The instance of the MainWindow class.
    """
    folder_path = QFileDialog.getExistingDirectory(None, "Select Folder", "/")
    name, ok = QInputDialog.getText(None, "File Prefix", "Enter the file prefix name:")

    if ok:
        name_prefix = name
    else:
        if config.config_get("Type") == "Tileset":
            name_prefix = "tile"
        elif config.config_get("Type") == "Icon Set":
            name_prefix = "icon"
        else:
            name_prefix = "item"

    if folder_path:
        app.progress_bar.move(app.width() // 2 - app.progress_bar.width() // 2, app.height() // 2 - app.progress_bar.height() // 2)
        app.progress_bar.setVisible(True)
        _current_value = 0

        for index in app.images:
            # Displays loop progression inside of a Progress Bar
            _current_value += 1
            progress = _current_value / len(app.images) * 100
            app.progress_bar.setValue(progress)

            if progress >= 100:
                app.progress_bar.setVisible(False)
                app.progress_bar.setValue(0)
                app.progress_bar.move(app.width(), app.height())

            if not has_pixel(get_image_at(app, index).pixmap().toImage()):
                continue

            img_path = os.path.join(folder_path, f"{name_prefix}_{index[1]}_{index[0]}.png")
            img = app.images[index]

            # Save each icon as an image file
            pixmap = img.pixmap()
            pixmap.save(img_path)

def save_all(app: 'classes.main_window.MainWindow') -> None:
    """
    Save the entire grid as a single image file.

    Args:
        - app: The instance of the MainWindow class.
    """
    # Get the file path to save the image
    file_path, _ = QFileDialog.getSaveFileName(None, "Save File", "", "PNG Files(*.png)")

    if file_path:
        _cell_size = app.cell_size
        width = maths.grid_col() * _cell_size
        height = (maths.max_row(app) + 1) * _cell_size

        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.drawPixmap(0, 0, pixmap)

        app.progress_bar.move(app.width() // 2 - app.progress_bar.width() // 2, app.height() // 2 - app.progress_bar.height() // 2)
        app.progress_bar.setVisible(True)
        _current_value = 0

        # Draw all the icons in the grid onto the pixmap
        for item in app.main_view.scene.items():
            # Displays loop progression inside of a Progress Bar
            _current_value += 1
            progress = _current_value / len(app.main_view.scene.items()) * 100
            app.progress_bar.setValue(progress)

            if progress >= 100:
                app.progress_bar.setVisible(False)
                app.progress_bar.setValue(0)
                app.progress_bar.move(app.width(), app.height())

            if isinstance(item, QGraphicsPixmapItem):
                pos = item.pos()
                pixmap_i = item.pixmap()
                item_pos = QPoint(int(pos.x()), int(pos.y()))
                painter.drawPixmap(item_pos, pixmap_i)

        painter.end()

        # Save the pixmap as an image file
        pixmap.save(file_path)

def play_animations(app: 'classes.main_window.MainWindow') -> None:
    if not app.main_view.highlight_selected[0]:
        return

    if not app.images:
        return

    _index = app.main_view.highlight_selected[1]
    group_index = None

    # Iterate over the grid
    for column in range(maths.grid_col()):
        for row in range(maths.grid_row()):
            # Calculate the group index based on the column and row values
            if _index == (column, row):
                group_index = (column // 3, row)
                break

    if group_index:
        _x = group_index[0] * 3
        _y = group_index[1]

        app.animation[1] = [
            get_image_at(app, (_x, _y)),
            get_image_at(app, (_x + 1, _y)),
            get_image_at(app, (_x + 2, _y)),
            get_image_at(app, (_x + 1, _y))
        ]

        image_index = 0  # Initialize the image index

        app.animation[0] = QTimer()
        app.animation[0].setInterval(200)

        update_image = partial(zoom, app)

        def handle_timeout():
            nonlocal image_index
            update_image(app.animation[1][image_index])
            image_index = (image_index + 1) % len(app.animation[1])

        app.animation[0].timeout.connect(handle_timeout)
        app.animation[0].start()

def stop_animations(app: 'classes.main_window.MainWindow') -> None:
    if app.animation[0]:
        app.animation[0].stop()
        app.animation[1] = None
