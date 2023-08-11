#!/usr/bin/env python
"""files.py"""
import os
import tempfile
from PySide6.QtCore import QDir, QPoint, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QFileDialog, QGraphicsPixmapItem, QInputDialog
from modules import config
from modules import grid_manager
from modules import maths
from modules import utils


def create_temp(app, image):
    """
    Create a temporary file from an image

    Args:
        - image: The image to create a temp for

    Returns:
        - str: The path of the temporary file
    """
    if not image:
        return None

    # Convert QGraphicsPixmapItem to an image
    if isinstance(image, QGraphicsPixmapItem):
        image = image.pixmap().toImage()

    # Check that we are not creating a temp for an "empty" image
    if not utils.has_valid_pixel(image):
        return None

    # Create a temporary file with the .png extension
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        app.temp.append(temp.name)
        image.save(temp.name)
        return temp.name


def create_temp_all(app):
    """
    Create a temporary file containing all the images in the grid.

    Args:
        - app: The application main window.

    Returns:
        - str: The path of the temporary file.
    """
    # Retrieve cell size attribute from the app
    cell_width, cell_height = app.cell_size

    # Check that we have item in the grid
    if app.images is None:
        return None

    # Calculate the width and height of the current grid state
    width = maths.grid_col() * cell_width
    height = (maths.max_row(app) + 1) * cell_height

    # Create a pixmap with those specifics size
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.drawPixmap(0, 0, pixmap)

    # Iterate over every items in the scene and draw them on the pixmap
    for item in app.main_view.scene.items():
        if isinstance(item, QGraphicsPixmapItem):
            pos = item.pos()
            pixmap_item = item.pixmap()
            item_pos = QPoint(pos.x(), pos.y())
            painter.drawPixmap(item_pos, pixmap_item)

    painter.end()

    # Create the temporary file with the .png extension
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        app.temp.append(temp.name)
        pixmap.save(temp.name)
        return temp.name


def save_highlighted_cell(app):
    """
    Save the selected cell as an image file.

    Args:
        - app: The application main window
    """
    # Prevent running if no cell is selected.
    if len(app.main_view.mass_highlight) > 0:
        images = []

        for highlight, index in app.main_view.mass_highlight:
            image = grid_manager.get_image_at(app, index)
            if image is None:
                continue

            images.append((image, index))  # Store both the image and the index

        if len(images) <= 0:
            return

        # Prompt for a folder to save file
        folder_path = QFileDialog.getExistingDirectory(
            None, "Select Folder", "/")

        if folder_path:
            # Prompt for a prefix for every saved files
            name, ok = QInputDialog.getText(
                None, "File Prefix", "Enter the file prefix name:")

            # If no prefix was input, give a default one
            if ok:
                name_prefix = name
            else:
                name_prefix = "image"

            # Display the progress bar
            app.progress_bar.move(
                app.width() // 2 - app.progress_bar.width() // 2,
                app.height() // 2 - app.progress_bar.height() // 2)
            app.progress_bar.setVisible(True)

            current_value = 0
            for image, index in images:  # Retrieve both the image and the index
                # Keep track of the methods progress
                current_value += 1
                progress = current_value / len(images) * 100
                app.progress_bar.setValue(progress)

                # Remove the progress bar if the methods reached the end
                if progress >= 100:
                    app.progress_bar.move(app.width(), app.height())
                    app.progress_bar.setVisible(False)
                    app.progress_bar.setValue(0)

                # Save the pixmap as a PNG file
                pixmap = image.pixmap()
                image_path = os.path.join(
                    folder_path, f"{name_prefix}_{index[1]}_{index[0]}.png")
                pixmap.save(image_path)

    elif app.main_view.highlight_selected[0]:
        # Retrieve the image
        image = grid_manager.get_image_at(
            app, app.main_view.highlight_selected[1])
        if image is None:
            return utils.show_popup("You cannot save an empty cell.", "INFO", ["OK"])

        # Get the file path to save the image
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save File", "", "PNG Files (*.png)")

        if file_path:
            # Save the pixmap as an png file
            pixmap = image.pixmap()
            pixmap.save(file_path)


def save_individually_each_cell(app):
    """
    Save each icon in the grid as individual image files.

    Args:
        - app: The application main window.
    """
    # Prevent running if there is no loaded image
    if not app.images:
        return utils.show_popup("You cannot save an empty image.", "INFO", ["OK"])

    # Prompt for a folder to save file
    folder_path = QFileDialog.getExistingDirectory(None, "Select Folder", "/")

    # Prompt for a prefix for every saved files
    name, ok = QInputDialog.getText(
        None, "File Prefix", "Enter the file prefix name:")

    # If no prefix was input, give a default one
    if ok:
        name_prefix = name
    else:
        name_prefix = "image"

    if folder_path:
        # Display the progress bar
        app.progress_bar.move(
            app.width() // 2 - app.progress_bar.width() // 2,
            app.height() // 2 - app.progress_bar.height() // 2)
        app.progress_bar.setVisible(True)

        current_value = 0

        # Loop through all item and save them
        for index in app.images:
            # Keep track of the methods progress
            current_value += 1
            progress = current_value / len(app.images) * 100
            app.progress_bar.setValue(progress)

            # Remove the progress bar if the methods reached the end
            if progress >= 100:
                app.progress_bar.move(app.width(), app.height())
                app.progress_bar.setVisible(False)
                app.progress_bar.setValue(0)

            # Check if the image contains "valid" pixels
            if not utils.has_valid_pixel(
                    grid_manager.get_image_at(app, index).pixmap().toImage()):
                continue

            image_path = os.path.join(
                folder_path, f"{name_prefix}_{index[1]}_{index[0]}.png")
            image = app.images[index]

            # Save each item as an image file
            pixmap = image.pixmap()
            pixmap.save(image_path)


def save_all_together(app):
    """
    Save the entire grid as a single image file.

    Args:
        - app: The application main window.
    """
    # Prevent running if there is no loaded image
    if not app.images:
        return utils.show_popup("You cannot save an empty image.", "INFO", ["OK"])

    # Get the file path to save the image
    file_path, _ = QFileDialog.getSaveFileName(
        None, "Save File", "", "PNG Files (*.png)")

    if file_path:
        # Retrieve cell width and height from the app
        cell_width, cell_height = app.cell_size

        if (config.config_get("type") == "Icons"):
            height = maths.max_row(app) * cell_height
        else:
            height = maths.grid_row() * cell_height

        width = maths.grid_col() * cell_width

        # Create the pixmap
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.drawPixmap(0, 0, pixmap)

        # Display the progress bar
        app.progress_bar.move(
            app.width() // 2 - app.progress_bar.width() // 2,
            app.height() // 2 - app.progress_bar.height() // 2)
        app.progress_bar.setVisible(True)

        current_value = 0

        # Loop through all item and save them
        for item in app.main_view.scene.items():
            # Keep track of the methods progress
            current_value += 1
            progress = current_value / len(app.main_view.scene.items()) * 100
            app.progress_bar.setValue(progress)

            # Remove the progress bar if the methods reached the end
            if progress >= 100:
                app.progress_bar.move(app.width(), app.height())
                app.progress_bar.setVisible(False)
                app.progress_bar.setValue(0)

            # Draw the QGraphicsPixmapItem to the pixmap
            if isinstance(item, QGraphicsPixmapItem):
                painter.drawPixmap(
                    QPoint(int(item.pos().x()), int(item.pos().y())),
                    item.pixmap()
                )

        painter.end()

        # Save the pixmap as an image file
        pixmap.save(file_path)


def prompt_file(app):
    """
    Open a file dialog to select an image file and returns it as a QImage

    Args:
        - app: The application main window.

    Returns:
        - QImage: QImage of the select file, otherwise None.
    """
    file_path, _ = QFileDialog.getOpenFileName(
        app,
        "Open File",
        "",
        "Image Files (*.png *.jpg *.jpeg *.gif)"
    )

    if file_path:
        return QImage(file_path)

    return None


def prompt_folder(app):
    """
    Open a folder dialog to select a folder

    Returns:
        - A tuple containing the directory object and a list of images
            file names in the selected folder or None if no folder is
            selected
    """
    # Open the folder dialog
    folder_path = QFileDialog.getExistingDirectory(
        None, "Select Input Folder", "/")
    directory = QDir(folder_path)

    # Set the filter and name filter to only include image files
    directory.setFilter(QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
    directory.setNameFilters(["*.png", "*.jpg", "*.jpeg", "*.gif"])

    # Return the directory object and a list of images file names in the folder
    return (directory, directory.entryList())
