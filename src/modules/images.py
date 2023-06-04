#================================================================================#
# File: images.py
# Created Date: 22-05-2023 | 13:31:11
# Author: Hereiti
#================================================================================
# Last Modified: 04-06-2023 | 01:20:44
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Imports
#================================================================================#
import tempfile
import os

from typing import Optional, Tuple

#================================================================================#
# Third-Party Imports
#================================================================================#
from PySide6.QtWidgets import QGraphicsPixmapItem, QFileDialog, QInputDialog
from PySide6.QtGui     import QPixmap, QImage, QColor, QPainter
from PySide6.QtCore    import QPoint

from PIL import Image, ImageQt, ImageCms

#================================================================================#
# Local Application Imports
#================================================================================#
from modules import utils, maths, config

#================================================================================#
# Functions
#================================================================================#
def create_temp(app: 'classes.MainWindow.MainWindow', image: Optional[QGraphicsPixmapItem]) -> Optional[str]:
    """
    Create a temporary file from the image.

    Args:
        image: The QGraphicsPixmapItem containing the image.

    Returns:
        str: The path of the temporary file.
    """
    if not image or not has_pixel(image.pixmap().toImage()):
        return None

    _temp = image.pixmap()

    # Create a temporary file with the .png extension
    if image is not None:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
            _temp.save(temp.name)
            app.temp_files.append(temp.name)
            return temp.name

    return None

def create_temp_all(app: 'classes.MainWindow.MainWindow') -> Optional[str]:
    """
    Create a temporary file containing all the images in the grid.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        str: The path of the temporary file.
    """
    _cell_size = maths.cell_size()
    if maths.max_col(app) > 0 or maths.max_row(app) > 0:
        width, height = maths.grid_col() * _cell_size, (maths.max_row(app) + 1) * _cell_size
    else:
        return None

    # Create a pixmap with the specified width and height
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.drawPixmap(0, 0, pixmap)

    # Iterate over items in the scene and draw their pixmaps onto the pixmap
    for item in app.main_view.scene.items():
        if isinstance(item, QGraphicsPixmapItem):
            pos = item.pos()
            pixmap_i = item.pixmap()
            item_pos = QPoint(int(pos.x()), int(pos.y()))
            painter.drawPixmap(item_pos, pixmap_i)

    painter.end()

    # Create a temporary file with the .png extension
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        pixmap.save(temp.name)
        app.temp_files.append(temp.name)
        return temp.name

def crop_image(image: QImage, origin: Tuple[int, int], size: int) -> QImage:
    """
    Crop a region from the given image.

    Args:
        image: The source image to crop.
        origin: The origin (top-left) position of the region to crop.
        size: The size of the region to crop.

    Returns:
        QImage: The cropped image.
    """
    # Copy a region from the source image based on the given origin and size
    return image.copy(*origin, size, size)

def has_pixel(image: QImage) -> bool:
    """
    Check if the given image has any fully opaque pixel.

    Args:
        image: The image to check.

    Returns:
        bool: True if the image has at least one fully opaque pixel, False otherwise.
    """
    # Convert QImage to PIL Image
    pil_image = Image.fromqpixmap(image)

    # Get the alpha channel of the image
    alpha = pil_image.split()[-1]

    # Check if there are any visible pixels (alpha = 25)
    return any(pixel >= 25 for pixel in alpha.getdata())

def image_at(app: 'classes.MainWindow.MainWindow', index: Tuple[int, int]) -> Optional[QGraphicsPixmapItem]:
    """
    Get the QGraphicsPixmapItem at the specified index in the app's icons dictionary.

    Args:
        app: The instance of the MainWindow class.
        index: The index of the item in the icons dictionary.

    Returns:
        Optional[QGraphicsPixmapItem]: The QGraphicsPixmapItem at the specified index, or None if not found.
    """
    if index in app.icons:
        # Return the QGraphicsPixmapItem at the specified index
        return app.icons[index]

    # Return None if the index is not found
    return None

def zoom(app: 'classes.MainWindow.MainWindow', item: Optional[QGraphicsPixmapItem]) -> None:
    """
    Zoom in on the specified QGraphicsPixmapItem.

    Args:
        app: The instance of the MainWindow class.
        item: The QGraphicsPixmapItem to zoom in on.

    Returns:
        None.
    """
    app.zoom_scene.clear()
    if item is not None:
        # Scale the pixmap to a fixed size for zooming
        pixmap = item.pixmap().scaled(160, 160)
        app.zoom_scene.addItem(QGraphicsPixmapItem(pixmap))

def save_selected(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Save the selected cell as an image file.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    if not app.main_view.highlight_selected:
        return

    _icon = image_at(app, app.main_view.highlight_selected[1])
    if _icon is None:
        return utils.show_popup("You cannot save an empty cell.", "INFO", ["OK"])

    # Get the file path to save the image
    file_path, _ = QFileDialog.getSaveFileName(None, "Save File", "", "PNG Files(*.png)")

    if file_path:
        # Save the pixmap as an image file
        pixmap = _icon.pixmap()
        pixmap.save(file_path)

def save_all(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Save the entire grid as a single image file.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    # Get the file path to save the image
    file_path, _ = QFileDialog.getSaveFileName(None, "Save File", "", "PNG Files(*.png)")

    if file_path:
        _cell_size = maths.cell_size()
        width, height = maths.grid_col() * _cell_size, (maths.max_row(app) + 1) * _cell_size

        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.drawPixmap(0, 0, pixmap)

        # Draw all the icons in the grid onto the pixmap
        for item in app.main_view.scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                pos = item.pos()
                pixmap_i = item.pixmap()
                item_pos = QPoint(int(pos.x()), int(pos.y()))
                painter.drawPixmap(item_pos, pixmap_i)

        painter.end()

        # Save the pixmap as an image file
        pixmap.save(file_path)

def save_individually(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Save each icon in the grid as individual image files.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    folder_path = QFileDialog.getExistingDirectory(None, "Select Folder", "/")
    name, ok = QInputDialog.getText(None, "File Prefix", "Enter the file prefix name:")

    if ok:
        name_prefix = name
    else:
        if config.get_config("Type") == "Tileset":
            name_prefix = "tile"
        elif config.get_config("Type") == "Icon Set":
            name_prefix = "icon"
        else:
            name_prefix = "item"

    if folder_path:
        for index in app.icons:

            if not has_pixel(image_at(app, index).pixmap().toImage()):
                continue

            icon_path = os.path.join(folder_path, f"{name_prefix}_{index[1]}_{index[0]}.png")
            icon = app.icons[index]

            # Save each icon as an image file
            pixmap = icon.pixmap()
            pixmap.save(icon_path)

            # Save each icon as an image file
            pixmap = icon.pixmap()
            pixmap.save(icon_path)

def convert_to_srgb(file_path: Optional[str]=None, image: Optional[QImage]=None) -> QImage:
    if file_path:
        pil_image = Image.open(file_path)
    else:
        # Convert the QImage to a PIL Image
        pil_image = ImageQt.fromqimage(image)

    # Create an sRGB profile
    srgb_profile = ImageCms.createProfile("sRGB")

    # Convert the PIL Image to the sRGB color space
    pil_image = ImageCms.profileToProfile(pil_image, srgb_profile, outputProfile=srgb_profile)

    # Convert the PIL Image back to a QImage
    return ImageQt.ImageQt(pil_image)
