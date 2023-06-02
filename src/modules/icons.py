#================================================================================#
# File: icons.py
# Created Date: 26-05-2023 | 19:28:22
# Author: Hereiti
#================================================================================
# Last Modified: 02-06-2023 | 11:25:18
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Imports
#================================================================================#
from typing import Tuple, Optional, List

#================================================================================#
# Third-Party Imports
#================================================================================#
from PySide6.QtCore    import QDir, Qt
from PySide6.QtGui     import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QFileDialog, QGraphicsPixmapItem

#================================================================================#
# Local Application Imports
#================================================================================#
from modules import edits, images, maths, utils

#================================================================================#
# Functions
#================================================================================#
def add(app: 'classes.MainWindow.MainWindow', image: QImage, index: Tuple[int, int]) -> None:
    """
    Add an image to the specified cell in the application.

    Args:
        app: The instance of the MainWindow class.
        image: The QImage to be added.
        index: The index of the cell.

    Returns:
        None.
    """
    # Convert QGraphicsPixmapItem to QImage
    if isinstance(image, QGraphicsPixmapItem):
        image = image.pixmap().toImage()

    # Check if the image has valid pixels
    if not images.has_pixel(image):
        return

    # Remove any existing image at the cell index and store the temporary path
    temp_path = remove(app, index)

    # Get the size of a cell
    cell_size = maths.cell_size()

    # Scale down the image if its dimensions exceed the cell size
    if image.width() > cell_size:
        image = image.scaled(cell_size, image.height())
    if image.height() > cell_size:
        image = image.scaled(image.width(), cell_size)

    # Create a pixmap and draw the image onto it
    pixmap = QPixmap(cell_size, cell_size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.drawImage(0, 0, image)
    painter.end()

    # Create a pixmap item and add it to the scene at the specified cell index
    pixmap_item = QGraphicsPixmapItem(pixmap)
    pixmap_item.setPos(*maths.origin(*index))
    app.main_view.scene.addItem(pixmap_item)

    # Update the icons dictionary with the new pixmap item at the cell index
    app.icons[index] = pixmap_item
    images.zoom(app, pixmap_item)

    # Add the action to the history
    edits.history(app, "ADD", index, temp_path)

def remove(app: 'classes.MainWindow.MainWindow', index: Tuple[int, int], history: bool = False) -> Optional[str]:
    """
    Remove the image at the specified cell index from the application.

    Args:
        app: The instance of the MainWindow class.
        index: The index of the cell.
        history: Whether to add the action to the history.

    Returns:
        The temporary path of the removed image, if available.
    """
    # Initialize the temporary path
    temp_path = None

    # Check if there is an image at the cell index
    if index in app.icons:
        item = app.icons[index]
        if item is not None:
            # Create a temporary image of the item and store its path
            temp_path = images.create_temp(app, item)

            # Remove the item from the scene and the icons dictionary
            app.main_view.scene.removeItem(item)
            del app.icons[index]

    # Add the action to the history if specified
    if history:
        edits.history(app, "DELETE", index, temp_path)

    images.zoom(app, None)

    return temp_path

def reset(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Reset the application by removing all pixmap items from the scene and clearing the icons dictionary.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    # Remove all pixmap items from the scene
    for item in app.main_view.scene.items():
        if not isinstance(item, QGraphicsPixmapItem):
            continue

        app.main_view.scene.removeItem(item)

    # Clear the icons dictionary
    app.icons = {}

def select_file(app: 'classes.MainWindow.MainWindow') -> Optional[QImage]:
    """
    Open a file dialog to select a PNG file and return it as a QImage.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        The selected QImage if a file is chosen, otherwise None.
    """
    # Open the file dialog to select a PNG file
    file_path, _ = QFileDialog.getOpenFileName(app, "Open File", "", "PNG Files (*.png)")

    if file_path:
        # Return the QImage of the selected file
        return QImage(file_path)

    return None

def select_folder() -> Optional[Tuple[QDir, List[str]]]:
    """
    Open a folder dialog to select a folder and return the directory object and a list of PNG file names in the folder.

    Returns:
        A tuple containing the directory object and a list of PNG file names in the selected folder,
        or None if no folder is selected.
    """
    # Open the folder dialog to select a folder
    folder_path = QFileDialog.getExistingDirectory(None, "Select Folder", "/")
    _dir = QDir(folder_path)

    # Set the filter and name filters to include only PNG files
    _dir.setFilter(QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
    _dir.setNameFilters(["*.png"])

    # Return the directory object and a list of PNG file names in the folder
    return (_dir, _dir.entryList())

def new(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Create a new project by resetting the application and clearing the undo/redo history.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    # Show a warning popup to confirm new project creation
    response = utils.show_popup("Any unsaved changes will be lost.\nDo you want to continue without saving ?", "WARNING", ["YES", "NO"])

    if response == "&No":
        return

    # Reset the application
    reset(app)

    _view = app.main_view
    _scene = _view.scene

    # Remove the highlight item if present
    if _view.highlight_selected:
        _scene.removeItem(_view.highlight_selected[0])
        _view.highlight_selected = None

    # Clear the undo/redo history
    app.undo = []
    app.redo = []

def load(app: 'classes.MainWindow.MainWindow', image: Optional[QImage] = None, history: bool = False) -> None:
    """
    Open an image in the application by creating pixmap items from the image and adding them to the scene.

    Args:
        app: The instance of the MainWindow class.
        image: The QImage to open in the application. If None, a file dialog will be shown to select an image.
        history: A flag indicating whether to create a history entry for the open operation.

    Returns:
        None.
    """
    cell_size = maths.cell_size()

    if image is None:
        # Select an image using the file dialog
        image = select_file(app)

    if image:
        if history:
            # Create a history entry for the open operation
            temp_path = images.create_temp_all(app)
            edits.history(app, "OVERHAUL", None, temp_path)

        # Reset the application by removing existing pixmap items
        reset(app)

        for column in range(maths.grid_col()):
            for row in range(min(image.height() // cell_size, maths.grid_row())):
                # Calculate the origin of the current cell
                cell_origin = maths.origin(column, row)

                # Crop the image to the cell size
                icon = images.crop_image(image, cell_origin, cell_size)

                # Skip empty icons without pixels
                if not images.has_pixel(icon):
                    continue

                # Create a pixmap with transparent background
                pixmap = QPixmap(cell_size, cell_size)
                pixmap.fill(Qt.GlobalColor.transparent)

                # Create a painter to draw the icon onto the pixmap
                painter = QPainter(pixmap)
                painter.drawImage(0, 0, icon)
                painter.end()

                # Create a pixmap item with the pixmap and set its position
                pixmap_item = QGraphicsPixmapItem(pixmap)
                pixmap_item.setPos(*cell_origin)

                # Add the pixmap item to the scene and store it in the icons dictionary
                app.main_view.scene.addItem(pixmap_item)
                app.icons[(column, row)] = pixmap_item

def sheet(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Add a sheet of images to the grid from a selected file.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    cell_size = maths.cell_size()
    row_i = maths.max_row(app) + 1

    _image = select_file(app)

    if _image:
        # If there are existing icons, create a history entry for the overhaul
        if app.icons:
            temp_path = images.create_temp_all(app)
            edits.history(app, "OVERHAUL", None, temp_path)

        for column in range(maths.grid_col()):
            for row in range(_image.height() // cell_size):
                # Calculate the origin of the current cell
                cell_origin = maths.origin(column, row)

                # Crop the image to get the icon for the current cell
                _icon = images.crop_image(_image, cell_origin, cell_size)

                # Skip empty icons without pixels
                if not images.has_pixel(_icon):
                    continue

                # Create a pixmap with transparent background
                pixmap = QPixmap(cell_size, cell_size)
                pixmap.fill(Qt.GlobalColor.transparent)

                # Create a painter to draw the icon onto the pixmap
                painter = QPainter(pixmap)
                painter.drawImage(0, 0, _icon)
                painter.end()

                # Calculate the new cell origin in the grid
                cell_origin = maths.origin(column, row_i + row)

                # Create a pixmap item with the pixmap and set its position
                pixmap_item = QGraphicsPixmapItem(pixmap)
                pixmap_item.setPos(*cell_origin)

                # Add the pixmap item to the scene and store it in the icons dictionary
                app.main_view.scene.addItem(pixmap_item)
                app.icons[(column, row_i + row)] = pixmap_item

def folder(app: 'classes.MainWindow.MainWindow') -> None:
    """
    Add images from a selected folder to the grid.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        None.
    """
    _dir, _images = select_folder()

    if len(_images) <= 0:
        return

    cell_size = maths.cell_size()

    # If there are existing icons, create a history entry for the overhaul
    if app.icons:
        temp_path = images.create_temp_all(app)
        edits.history(app, "OVERHAUL", None, temp_path)

    col_i, row_i = 1, maths.max_row(app) + 1
    grid_col, grid_row = maths.grid_col(), maths.grid_row() + 1
    _images = sorted(_images, key=utils.numerical_sort_key)

    for index, file_name in enumerate(_images):
        _icon_path = _dir.absoluteFilePath(file_name)

        # Move to the next row if the current column is the last column of the grid
        if (index + 1) % grid_col == 0:
            row_i += 1
            col_i = 0

        # If the next row exceeds the maximum row count, stop adding icons
        if row_i > grid_row:
            return

        # Calculate the origin of the current cell
        cell_origin = maths.origin(col_i, row_i)
        _icon = QImage(_icon_path)

        # Skip images without pixels
        if not images.has_pixel(_icon):
            return

        # Scale the image if it exceeds the cell size
        if _icon.width() > cell_size:
            _icon = _icon.scaled(cell_size, _icon.height())
        if _icon.height() > cell_size:
            _icon = _icon.scaled(_icon.width(), cell_size)

        # Create a pixmap with transparent background
        pixmap = QPixmap(cell_size, cell_size)
        pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter to draw the icon onto the pixmap
        painter = QPainter(pixmap)
        painter.drawImage(0, 0, _icon)
        painter.end()

        # Create a pixmap item with the pixmap and set its position
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setPos(*cell_origin)

        # Add the pixmap item to the scene and store it in the icons dictionary
        app.main_view.scene.addItem(pixmap_item)
        app.icons[(col_i, row_i)] = pixmap_item

        col_i += 1
