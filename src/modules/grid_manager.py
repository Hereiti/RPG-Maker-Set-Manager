#!/usr/bin/env python
"""grid_manager.py"""
import textwrap
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QDialog, QGraphicsPixmapItem
from classes.dialogs import TwoInputs, FourInputs
from classes.item_highlight import Highlight
from modules import config
from modules import files
from modules import image_manipulation
from modules import maths
from modules import utils


def click_cell(event, app, modif=None):
    """
    Handle the click event on a cell.

    This function is called when a cell is clicked in the main view.

    Args:
        - event: The mouse event triggered by the click.
        - app: The application main window.
    """
    # Retrieve main_view and cell_size from the app
    main_view = app.main_view
    cell_width, cell_height = app.cell_size

    # Map the event position to scene coordinates
    scene_pos = main_view.mapToScene(event.pos())
    x, y = scene_pos.x(), scene_pos.y()

    # Calculate the cell index and origin
    cell_index = maths.cell_index(x, y)
    cell_origin = maths.cell_origin(cell_index)

    # Check if the click is out of grid bounds
    limit = maths.cell_origin((maths.grid_col() - 1, maths.grid_row() - 1))
    if any(coord < 0 or coord > limit for coord, limit, in zip(cell_origin, limit)):
        return

    if modif == "mass":
        if main_view.highlight_selected[0]:
            main_view.mass_highlight.append((
                main_view.highlight_selected[0], main_view.highlight_selected[1]))
            main_view.unique_index.append((main_view.highlight_selected[1]))
            main_view.mass_highlight[-1][0].reset_timer()
            main_view.highlight_selected = [None, None]

        # Check that the cell index is unique to prevent overlapping highlight.
        if cell_index not in main_view.unique_index:
            # Add the highlight to the list and scene.
            main_view.mass_highlight.append((
                Highlight("red", cell_width, cell_height), cell_index))
            main_view.scene.addItem(main_view.mass_highlight[-1][0])
            main_view.mass_highlight[-1][0].setZValue(2)
            main_view.mass_highlight[-1][0].setOpacity(0.5)
            main_view.mass_highlight[-1][0].setPos(*cell_origin)

            # Make sure that every highlights blink at the same time.
            for highlight, index in main_view.mass_highlight:
                highlight.reset_timer()

            # Add the index to a list for comparaison.
            main_view.unique_index.append((cell_index))

    elif modif is None:
        # Check if there is already a highlight.
        if len(main_view.mass_highlight) > 0:
            for highlight, index in main_view.mass_highlight:
                main_view.scene.removeItem(highlight)

            main_view.mass_highlight.clear()
            main_view.unique_index.clear()

        if main_view.highlight_selected[0] is None:
            main_view.highlight_selected = [
                Highlight("red", cell_width, cell_height),
                cell_index
            ]
            main_view.scene.addItem(main_view.highlight_selected[0])
            main_view.highlight_selected[0].setZValue(2)
            main_view.highlight_selected[0].setOpacity(0.5)

        # Set the position and index of the highlight item
        main_view.highlight_selected[1] = cell_index
        main_view.highlight_selected[0].setPos(*cell_origin)
        main_view.highlight_selected[0].reset_timer()

        # Check if animations are already being played
        if app.animation and app.animation[1] is not None:
            image_manipulation.stop_animation(app)

        # Update the main window label
        num = cell_index[1] * 16 + cell_index[0]
        app.labels["Index"].setText(
            f"● [{cell_index[0]}:{cell_index[1]}] - Cell n°{num} ●"
        )


def highlight_index(app, cell_index, modif=None):
    """
    Highlights the given index cell.

    Args:
        - app: The application main window
        - index: The index of the cell to highlight
    """
    # Retrieve main_view and cell_size from the app
    main_view = app.main_view
    cell_width, cell_height = app.cell_size

    # Calculate the cell origin
    cell_origin = maths.cell_origin(cell_index)

    # Check if the click is out of grid bounds
    limit = maths.cell_origin((maths.grid_col() - 1, maths.grid_row() - 1))
    if any(coord < 0 or coord > limit for coord, limit, in zip(cell_origin, limit)):
        return

    if modif == "mass":
        if main_view.highlight_selected[0]:
            main_view.mass_highlight.append((
                main_view.highlight_selected[0], main_view.highlight_selected[1]))
            main_view.unique_index.append((main_view.highlight_selected[1]))
            main_view.mass_highlight[-1][0].reset_timer()
            main_view.highlight_selected = [None, None]

        # Check that the cell index is unique to prevent overlapping highlight.
        if cell_index not in main_view.unique_index:
            # Add the highlight to the list and scene.
            main_view.mass_highlight.append((
                Highlight("red", cell_width, cell_height), cell_index))
            main_view.scene.addItem(main_view.mass_highlight[-1][0])
            main_view.mass_highlight[-1][0].setZValue(2)
            main_view.mass_highlight[-1][0].setOpacity(0.5)
            main_view.mass_highlight[-1][0].setPos(*cell_origin)

            # Make sure that every highlights blink at the same time.
            for highlight, index in main_view.mass_highlight:
                highlight.reset_timer()

            # Add the index to a list for comparaison.
            main_view.unique_index.append((cell_index))
            main_view.mass_highlight = sorted(
                main_view.mass_highlight, key=lambda x: (x[1][0], x[1][1]))

    if modif is None:
        # Check if there is already a highlight.
        if len(main_view.mass_highlight) > 0:
            for highlight, index in main_view.mass_highlight:
                main_view.scene.removeItem(highlight)

            main_view.mass_highlight.clear()
            main_view.unique_index.clear()

        if main_view.highlight_selected[0] is None:
            main_view.highlight_selected = [
                Highlight("red", cell_width, cell_height),
                cell_index
            ]
            main_view.scene.addItem(main_view.highlight_selected[0])
            main_view.highlight_selected[0].setZValue(2)
            main_view.highlight_selected[0].setOpacity(0.5)

        # Set the position and index of the highlight item
        main_view.highlight_selected[0].setPos(*cell_origin)
        main_view.highlight_selected[0].reset_timer()
        main_view.highlight_selected[1] = cell_index

        # Update the main window label
        num = cell_index[1] * 16 + cell_index[0]
        app.labels["Index"].setText(
            f"● [{cell_index[0]}:{cell_index[1]}] - Cell n°{num} ●"
        )


def get_image_at(app, index):
    """
    Get the QGraphicsPixmapItem at the specified index in the app
    images dictionary.

    Args:
        - app: The application main window.
        - index: The index of the cell to retrieve the image from.
    """
    if index in app.images:
        # Return the QGraphicsPixmapItem at the specified index
        return app.images[index]

    # Return None if the index is not present
    return None


def get_weapon_layer(app, index):
    """
    Get the QGraphicsPixmapItem at the specified index in the app
    images dictionary.

    Args:
        - app: The application main window.
        - index: The index of the cell to retrieve the image from.
    """
    if index in app.weapons:
        # Return the QGraphicsPixmapItem at the specified index
        return app.weapons[index]

    # Return None if the index is not present
    return None


def add_to_grid(app, image, index, history=True):
    """
    Add an image at the specified grid index in the main_view scene.

    Args:
        - app: The application main window.
        - image: The QImage to be added
        - index: The index of the cell
    """
    if not image:
        return

    # Prevent continuing if a thread is running
    if isinstance(image, QGraphicsPixmapItem):
        image = image.pixmap().toImage()

    # Check if the image contains "valid" pixels
    if not utils.has_valid_pixel(image):
        return

    # Remove any existing image at the index
    temp_path = remove_from_grid(app, index)

    # Retrieve cell width and height
    cell_width, cell_height = app.cell_size

    # Scale down the image if its dimensions exceed the cell size
    if image.width() > cell_width:
        image = image.scaled(
            cell_width,
            image.height(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    if image.height() > cell_height:
        image = image.scaled(
            image.width(),
            cell_height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    # Create a pixmap and draw the image onto it
    pixmap = QPixmap(cell_width, cell_height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.drawImage(0, 0, image)
    painter.end()

    # Create a pixmap item and add it to the scene
    pixmap_item = QGraphicsPixmapItem(pixmap)
    pixmap_item.setPos(*maths.cell_origin(index))
    app.main_view.scene.addItem(pixmap_item)

    # Update the images dictionary
    app.images[index] = pixmap_item

    # Add the action to the actions history
    if history:
        utils.history(app, "ADD", index, temp_path)


def remove_from_grid(app, index, history=False):
    """
    Remove the image at the specified cell index from the application.

    Args:
        app: The instance of the MainWindow class.
        index: The index of the cell.
        history: Whether to add the action to the history.

    Returns:
        The temporary path of the removed image, if available.
    """
    # Prevent continuing if a thread is running
    if app.thread_running:
        return

    # Check if there is an image at the cell index
    if index not in app.images:
        return

    item = app.images[index]
    temp_path = files.create_temp(app, item)
    app.main_view.scene.removeItem(item)
    del app.images[index]

    # Add the action to the actions history
    if history:
        utils.history(app, "DELETE", index, temp_path)

    return temp_path


def clear_main_view(app):
    """
    Remove every images contained in the main scene.

    Args:
        - app: The instance of the main window class
    """
    # Prevent running if a thread is already running
    if app.thread_running:
        return

    # Remove all images from the main view
    for item in app.main_view.scene.items():
        if not isinstance(item, QGraphicsPixmapItem):
            continue
        app.main_view.scene.removeItem(item)
    app.images.clear()
    app.weapons.clear()


def new(app):
    """
    Create a new project by resetting the application and clearing the history.

    Args:
        - app: The application main window
    """
    # Prevent running if a thread is running
    if app.thread_running:
        return

    # Show a warning popup to confirm this action
    response = utils.show_popup(textwrap.dedent("""
            Any unsaved changes will be lost.
            Do you want to continue without saving ?
        """), "WARNING", ["YES", "NO"])

    if response != "&Yes":
        return

    # Remove every images
    clear_main_view(app)

    # Remove the highlight cell if there is one
    if app.main_view.highlight_selected[0]:
        app.main_view.scene.removeItem(app.main_view.highlight_selected[0])
        app.main_view.highlight_selected = [None, None]

    # Reset histories
    app.undo.clear()
    app.redo.clear()


def load(app, image=None, history=True, reset=False, index=None):
    """
    Open an image in the application by creating pixmap items from the image.

    Args:
        - app: The application main window.
        - image: The image to open in the application.
        - history: A flag indicating whether to create a history entry or not.
        - reset: Should the scene be reset before loading the new image.
        - index: Where should the loop starts.
    """
    # Prevent running if a thread is already running
    if app.thread_running:
        return

    # Retrieve cell size from the app
    cell_width, cell_height = app.cell_size

    if not image:
        # Prompt for a .png file
        image = files.prompt_file(app)

    if not image:
        return

    if history and app.images:
        # Create a history entry
        temp_path = files.create_temp_all(app)
        utils.history(app, "OVERHAUL", None, temp_path)

    if reset:
        clear_main_view(app)

    # Display the progress bar
    max_value = maths.grid_col() * max(min(
        image.height() // cell_height, maths.grid_row()), 1)
    app.progress_bar.setVisible(True)
    current_value = 0

    for column in range(maths.grid_col()):
        for row in range(max(min(
                image.height() // cell_height + 1, maths.grid_row()), 1)):
            # Calculate the origin of the cell
            cell_origin = maths.cell_origin((column, row))

            # Crop the image to the cell size
            crop_image = image.copy(*cell_origin, cell_width, cell_height)

            # Display the loop progress inside of the progress bar
            current_value += 1
            progress = current_value / max_value * 100
            app.progress_bar.setValue(progress)

            # Remove the progress bar once the loop reached the last value
            if progress >= 100:
                app.progress_bar.setVisible(False)
                app.progress_bar.setValue(0)

            # Skip "empty" image
            if not utils.has_valid_pixel(crop_image):
                continue

            # Calculate the grid cell origin
            cell_index = (column, row)
            if index:
                cell_index = (column + index[0], row + index[1])
            cell_origin = maths.cell_origin(cell_index)

            # Check if the cell is out of bounds
            limit = maths.cell_origin(
                (maths.grid_col() - 1, maths.grid_row() - 1))
            if any(coord < 0 or coord > limit
                    for coord, limit, in zip(cell_origin, limit)):
                continue

            # Create a pixmap
            pixmap = QPixmap(cell_width, cell_height)
            pixmap.fill(Qt.GlobalColor.transparent)

            # Create a painter to draw image onto the pixmap
            painter = QPainter(pixmap)
            painter.drawImage(0, 0, crop_image)
            painter.end()

            if cell_index in app.images:
                app.main_view.scene.removeItem(app.images[cell_index])
                del app.images[cell_index]

            # Create a pixmap item and set its position
            pixmap_item = QGraphicsPixmapItem(pixmap)
            pixmap_item.setPos(*cell_origin)

            # Adds it to the main scene and app dict
            app.main_view.scene.addItem(pixmap_item)
            app.images[cell_index] = pixmap_item


def add_after(app):
    """
    Add images to the row following the lowest item.

    Args:
        - app: The application main window.
    """
    # Prevent running if a thread is running
    if app.thread_running:
        return

    index = (0, maths.max_row(app) + 1)
    load(app=app, history=True, index=index)


def load_folder(app):
    """
    Add images from a selected folder to the grid.

    Args:
        - app: The application main window.
    """
    # Prevent running if a thread is running
    if app.thread_running:
        return

    directory, images = files.prompt_folder(app)
    if len(images) <= 0:
        return

    # Retrieve cell size from the app
    cell_width, cell_height = app.cell_size

    # Create a temp if there are images loaded
    if app.images:
        temp_path = files.create_temp_all(app)
        utils.history(app, "OVERHAUL", None, temp_path)

    col, row = 0, maths.max_row(app)
    grid_col = maths.grid_col()
    grid_row = maths.grid_row() + 1

    # Display the progress bar
    app.progress_bar.setVisible(True)

    images = sorted(images, key=utils.numerical_sort)
    for index, filename in enumerate(images):
        image_path = directory.absoluteFilePath(filename)

        # Move to the next row if the current column is the last
        if (index) % grid_col == 0:
            row += 1
            col = 0

        # If the next rows exceed the max row count, stop adding image
        if row > grid_row:
            app.progress_bar.setValue(0)
            app.progress_bar.setVisible(False)
            break

        # Load the image as a QImage
        image = QImage(image_path)

        # Display loop progress
        progress = (index + 1) / len(images) * 100
        app.progress_bar.setValue(progress)

        # Remoeve the progress bar as needed
        if progress >= 100:
            app.progress_bar.setValue(0)
            app.progress_bar.setVisible(False)

        # Skip if the image has no "valid" pixels
        if not utils.has_valid_pixel(image):
            return

        # Scale the image if it exceed the cell size
        if image.width() > cell_width:
            image = image.scaled(cell_width, image.height())
        if image.height() > cell_height:
            image = image.scaled(image.width(), cell_height)

        # Create a pixmap
        pixmap = QPixmap(cell_width, cell_height)
        pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter to draw the image onto our pixmap
        painter = QPainter(pixmap)
        painter.drawImage(0, 0, image)
        painter.end()

        # Calculate the origin from the index
        cell_origin = maths.cell_origin((col, row))

        # Create a pixmap item and set its position
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setPos(*cell_origin)

        # Add the pixmap item to the main scene and app dict
        app.main_view.scene.addItem(pixmap_item)
        app.images[(col, row)] = pixmap_item

        # Increase for the next iteration
        col += 1


def custom_grid(app):
    dialog = FourInputs(
        title="Custom Grid",
        label_1="Grid Column", value_1="16",
        label_2="Grid Row", value_2="8",
        label_3="Cell Width", value_3="32",
        label_4="Cell Height", value_4="32")
    if dialog.exec() == QDialog.Accepted:
        # Retrieve the values from the text boxes
        column = dialog.textbox_1.text()
        row = dialog.textbox_2.text()
        cell_width = dialog.textbox_3.text()
        cell_height = dialog.textbox_4.text()

        # Show a warning popup to confirm whether to continue without saving.
        response = utils.show_popup(
            "Any unsaved changes will be lost.\nDo you want to continue ?",
            "WARNING", ["YES", "NO"]
        )

        if response == "&No":
            return

        config.config_set("GRID COLUMNS", column)
        config.config_set("GRID ROWS", row)
        config.config_set("CELL SIZE", f"{cell_width}x{cell_height}")
        config.config_set("CREATOR", "None")
        config.config_set("TYPE", "Custom")

        # Restart the application
        from main import restart
        restart()


def custom_cell_size(app):
    dialog = TwoInputs(
        title="Custom Cell Size",
        label_1="Cell Width", value_1="32",
        label_2="Cell Height", value_2="32")

    if dialog.exec() == QDialog.Accepted:
        # Retrieve the values from the text boxes
        cell_width = dialog.textbox_1.text()
        cell_height = dialog.textbox_2.text()

        # Show a warning popup to confirm whether to continue without saving.
        utils.config_changes_restart(
            app, "CELL SIZE", f"{cell_width}x{cell_height}")
