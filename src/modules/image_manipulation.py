#!/usr/bin/env python
"""image_manipulation.py"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QDialog, QInputDialog, QGraphicsPixmapItem
from classes.dialogs import TwoInputs
from PIL import Image
from modules import config
from modules import files
from modules import grid_manager
from modules import maths


def zoom(app, item, layer=0, reset=True):
    """
    Zoom in on the specified QGraphicsPixmapItem.

    Args:
        - app: The application main window.
        - item: The QGraphicsPixmapItem to zoom in on.
    """
    if reset:
        app.zoom_scene.clear()
    if item is not None:
        # Scale the pixmap to the desired width and height with the best quality
        if not isinstance(item, QPixmap):
            item = item.pixmap()

        image = Image.fromqimage(item.toImage())
        if config.config_get("TYPE") == "Weapons":
            image = image.resize((240, 160), resample=Image.NEAREST)
        else:
            image = image.resize((160, 160), resample=Image.NEAREST)
        item = QGraphicsPixmapItem(QPixmap.fromImage(image.toqimage()))
        item.setZValue(layer)
        app.zoom_scene.addItem(item)


def play_animation(app):
    """
    Play a X frames animations.

    Args:
        - app: The application main window
    """
    if not app.main_view.highlight_selected[0]:
        return

    if not app.images:
        return

    index = app.main_view.highlight_selected[1]
    group_index = None

    creator = config.config_get("CREATOR")
    type_ = config.config_get("TYPE")

    # Iterate over the grid
    for column in range(maths.grid_col()):
        for row in range(maths.grid_row()):
            # Calculate the group index based on the column and row values
            if index == (column, row):
                if creator == "None":
                    if type_ in ["States", "Balloons"]:
                        group_index = (column // 8, row)
                    else:
                        group_index = (column // 3, row)
                if creator == "Holder":
                    group_index = (column // 4, row)
                break

    if group_index:
        if creator == "None":
            if type_ in ["States", "Balloons"]:
                x = group_index[0] * 8
                y = group_index[1]

                app.animation[1] = [
                    (x, y), (x + 1, y), (x + 2, y),
                    (x + 3, y), (x + 4, y), (x + 5, y),
                    (x + 6, y), (x + 7, y)]

            else:
                x = group_index[0] * 3
                y = group_index[1]

                app.animation[1] = [(x, y), (x + 1, y), (x + 2, y)]

        if creator == "Holder":
            x = group_index[0] * 4
            y = group_index[1]

            app.animation[1] = [(x, y), (x + 1, y), (x + 2, y), (x + 3, y)]

        # Initialize the image index
        image_index = 0

        # Create a timer for the animation loop
        app.animation[0] = QTimer()
        app.animation[0].setInterval(140)

        def animation_timeout():
            nonlocal image_index
            grid_manager.highlight_index(app, app.animation[1][image_index])
            image_index = (image_index + 1) % len(app.animation[1])

        app.animation[0].timeout.connect(animation_timeout)
        app.animation[0].start()


def stop_animation(app):
    if app.animation[0]:
        app.animation[0].stop()
        app.animation = [None, None]


def offset(app, direction=None, x=None, y=None):
    """
    Offset the icon in the selected cell by one pixel in the specified
    direction.

    Args:
        - app: The application main window.
        - direction: The direction to offset the icon.
            Possible values: "RIGHT", "LEFT", "DOWN", "UP".
    """
    # Check if there is a selected cell
    if not app.main_view.highlight_selected[0]:
        return

    # Get the index of the cell
    index = app.main_view.highlight_selected[1]

    # Check if the index exists in the images dictionary
    if index in app.images:
        # Get the images as a pixmap
        image_pixmap = app.images[index].pixmap()

        # Create a new pixmap
        offset_pixmap = QPixmap(*app.cell_size)
        offset_pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter to draw on the pixmap
        painter = QPainter(offset_pixmap)

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
            if x:
                offset_x = x
            if y:
                offset_y = y

        # Draw the offset pixmap by applying the offset values
        painter.drawPixmap(offset_x, offset_y, image_pixmap)
        painter.end()

        # Create a new pixmap item with the offset pixmap
        pixmap_item = QGraphicsPixmapItem(offset_pixmap)
        grid_manager.add_to_grid(app, pixmap_item, index)


def change_offset(app):
    """
    Offset the icon in the selected cell by one pixel by the specified value.

    Args:
        - app: The application main window.
    """
    # Prevent running if there is no selected cell
    if not app.main_view.highlight_selected[0]:
        return

    if not grid_manager.get_image_at(app, app.main_view.highlight_selected[1]):
        return

    # Retrieve cell width and height from the app
    cell_width, cell_height = app.cell_size

    dialog = TwoInputs(
        title="Offset",
        label_1=f"Offset X (-{cell_width}:{cell_width}):",
        value_1="0",
        label_2=f"Offset Y (-{cell_height}:{cell_height}):",
        value_2="0")

    if dialog.exec() == QDialog.Accepted:
        # Retrieve values from the text boxes
        offset_x = dialog.textbox_1.text()
        offset_y = dialog.textbox_2.text()

        if ((
            offset_x.startswith("-") and offset_x[1:].isdigit()
                or offset_x.isdigit()
        ) and (
            offset_y.startswith("-") and offset_y[1:].isdigit()
                or offset_y.isdigit())):
            offset_x = int(offset_x)
            offset_y = int(offset_y)
        else:
            return

        offset(app=app, x=offset_x, y=offset_y)


def change_hue(app):
    """
    Interact with the slider to change the hue.

    Args:
        - app: The application main window
    """
    # Prevent running if there is no selected cell
    if not app.main_view.highlight_selected[0]:
        return

    if not grid_manager.get_image_at(app, app.main_view.highlight_selected[1]):
        return

    value, ok = QInputDialog.getText(
        None, "Image Hue",
        "Enter the new hue value (0-359):", text=str(app.last_hsv["hue"]))

    if not ok:
        return

    if value.isdigit():
        value = int(value)
        if value > 359 or value < 0:
            return

        hue_slider = app.sliders["Hue"]
        hue_slider.change_hsv(app, value, "hue")
        hue_slider.on_slider_end(app)


def change_saturation(app):
    """
    Interact with the slider to change the saturation.

    Args:
        - app: The application main window
    """
    # Prevent running if there is no selected cell
    if not app.main_view.highlight_selected[0]:
        return

    if not grid_manager.get_image_at(app, app.main_view.highlight_selected[1]):
        return

    value, ok = QInputDialog.getText(
        None, "Image Saturation",
        "Enter the new saturation value (0-255):", text=str(app.last_hsv["saturation"]))

    if not ok:
        return

    if value.isdigit():
        value = int(value)
        if value > 255 or value < 0:
            return

        saturation_slider = app.sliders["Saturation"]
        saturation_slider.change_hsv(app, value, "saturation")
        saturation_slider.on_slider_end(app)


def change_value(app):
    """
    Interact with the slider to change the value.

    Args:
        - app: The application main window
    """
    if not app.main_view.highlight_selected[0]:
        return

    if not grid_manager.get_image_at(app, app.main_view.highlight_selected[1]):
        return

    value, ok = QInputDialog.getText(
        None, "Image Brightness",
        "Enter the new brightness value (-255-255):", text=str(app.last_hsv["value"]))

    if not ok:
        return

    if value.isdigit() or value.startswith("-") and value[1:].isdigit():
        value = int(value)
        if value > 255 or value < -255:
            return

        value_slider = app.sliders["Value"]
        value_slider.change_hsv(app, value, "value")
        value_slider.on_slider_end(app)


def flip_image(app, orientation):
    """
    Flip the image based on the specified orientation.

    Args:
        - app: The application main window
        - orientation: The orientation to flip the image;
            can be Horizontal or Vertical
    """
    # Check if there is a selected cell
    if not app.main_view.highlight_selected[0]:
        return

    if not grid_manager.get_image_at(app, app.main_view.highlight_selected[1]):
        return

    # Get the index of the cell
    index = app.main_view.highlight_selected[1]

    # Check if the index exists in the images directory
    if index in app.images:
        # Get the image from the cell
        image = app.images[index].pixmap().toImage()

        # Transform the image
        transform = QTransform()
        if orientation == "Vertical":
            transform.scale(-1, 1)
        elif orientation == "Horizontal":
            transform.scale(1, -1)
        else:
            return

        flipped_image = image.transformed(transform)
        grid_manager.add_to_grid(app, flipped_image, index)


def change_color(app, color=None):
    """
    Interact with the slider to change the value.

    Args:
        - app: The application main window
        - color: The color to modify (can be Red, Green or Blue)
    """
    # Prevent running if no color is specified
    if not color:
        return

    # Prevent running if there is no selected cell
    if not app.main_view.highlight_selected[0]:
        return

    if not grid_manager.get_image_at(app, app.main_view.highlight_selected[1]):
        return

    value, ok = QInputDialog.getText(
        None, "Specified Color",
        f"Enter the value for the {color} color (-255-255):",
        text=str(app.last_rgb[color])
    )

    if not ok:
        return

    if value.isdigit() or value.startswith("-") and value[1:].isdigit():
        value = int(value)
        if value > 255 or value < -255:
            return

        if color == "red":
            red_slider = app.sliders["Red"]
            red_slider.change_rgb(app, value, "red")
            red_slider.on_slider_end(app)
        elif color == "green":
            green_slider = app.sliders["Green"]
            green_slider.change_rgb(app, value, "green")
            green_slider.on_slider_end(app)
        elif color == "blue":
            blue_slider = app.sliders["Blue"]
            blue_slider.change_rgb(app, value, "blue")
            blue_slider.on_slider_end(app)


def copy(app):
    """
    Copy the selected cell image.

    Args:
        - app: The application main window.
    """
    # Prevent running if there is no selected cell
    if not app.main_view.highlight_selected[0]:
        return

    # Check if the cell index exists in the images dict
    index = app.main_view.highlight_selected[1]
    if index in app.images:
        # Store it inside of the app attribute
        app.copied_image = app.images[index]


def cut(app):
    """
    Copy then remove the image from the selected cell.

    Args:
        - app: The application main window.
    """
    # Check if there is a selected cell
    if not app.main_view.highlight_selected[0]:
        return

    # Check if the cell index exists in the images dict
    index = app.main_view.highlight_selected[1]
    if index in app.images:
        # Copy the image then removes it
        copy(app)
        grid_manager.remove_from_grid(app, index, True)


def paste(app):
    """
    Paste the copied image onto the selected cell.

    Args:
        - app: The application main window
    """
    # Prevent running if there is no selected cell nor copied image
    if app.main_view.highlight_selected[0] and app.copied_image:
        # Get the index of the selected cell
        index = app.main_view.highlight_selected[1]
        grid_manager.add_to_grid(app, app.copied_image, index)


def undo(app):
    """
    Undo the last action in application undo history

    Args:
        - app: The application main window.
    """
    # Retrieve app attributes
    undo = app.undo
    redo = app.redo
    images = app.images
    main_view = app.main_view

    # Check if there is any action to undo
    if not undo:
        return

    # Retrieve the last action from the undo list
    last_action = undo.pop()
    type_, index, temp = last_action[:3]

    if type_ in ["ADD", "DELETE"]:
        # Calculate the cell origin based on the index
        cell_origin = maths.cell_origin(index)

        if type_ == "ADD":
            # Check if there is an item at the current index and removes it
            item = images[index]
            temp_path = None
            if item:
                temp_path = grid_manager.remove_from_grid(app, index)

            # Check if there was an image before the action
            if temp:
                pixmap_item = QGraphicsPixmapItem(QPixmap(temp))
                main_view.scene.addItem(pixmap_item)
                pixmap_item.setPos(*cell_origin)
                images[index] = pixmap_item

            # Append this action into the redo list
            redo.append(("ADD", index, temp_path, None))

        if type_ == "DELETE":
            # Check if there was an image before the action
            grid_manager.add_to_grid(app, QImage(temp), index, False)

            # Append this action into the redo list
            redo.append(("DELETE", index, None, None))

        # Create or move the highlight to this cell
        grid_manager.highlight_index(app, index)

    elif type_ == "MOVE":
        # Retrieve both indexes from the action argument
        index_a, index_b = index

        # Retrieve the move type of the last action
        move_type = last_action[3]

        if move_type == "SWITCH":
            # Retrieve the pixmap items corresponding to the cell indexes
            item_a = images.get(index_a)
            item_b = images.get(index_b)

            # Calculate cell origins based on the indexes
            origin_a = maths.cell_origin(index_a)
            origin_b = maths.cell_origin(index_b)

            if item_a:
                item_a.setPos(*origin_b)
                images[index_b] = item_a

            if item_b:
                item_b.setPos(*origin_a)
                images[index_a] = item_b

        elif move_type == "OVERWRITE":
            # Retrieve the pixmap item corresponding to index_b
            images[index_a] = images[index_b]
            del images[index_b]
            item = images[index_a]
            item.setPos(*maths.cell_origin(index_a))

            if temp:
                grid_manager.add_to_grid(app, QImage(temp), index_b, False)

        # Add the action to the redo list
        redo.append(("MOVE", index, None, move_type))

        # Create or move the highlight to the index
        grid_manager.highlight_index(app, index_a)

    elif type_ == "OVERHAUL":
        # Create a temp of the full view
        temp_path = files.create_temp_all(app)

        if temp:
            # Open the image and replace all images
            grid_manager.load(
                app, QImage(temp), False, True)
        else:
            # Remove all images
            grid_manager.clear_main_view(app)

        # Add the action to the redo list
        redo.append(("OVERHAUL", None, temp_path))


def redo(app):
    """
    Redo the last undone action in the redo history

    Args:
        - app: The application main window.
    """
    undo = app.undo
    redo = app.redo
    images = app.images

    # Prevent running if the redo history is empty
    if not redo:
        return

    # Retrieve the last action from the redo list
    last_action = redo.pop()
    type_, index, temp = last_action[:3]

    if type_ in ["ADD", "DELETE"]:
        if type_ == "ADD":
            temp_path = grid_manager.remove_from_grid(app, index)

            # Add back the previous image
            grid_manager.add_to_grid(app, QImage(temp), index, False)

            # Add the action back into the undo list
            undo.append(("ADD", index, temp_path, None))

        if type_ == "DELETE":
            # Remove the image at the specified index
            temp_path = grid_manager.remove_from_grid(app, index)

            # Add the action back into the undo list
            undo.append(("DELETE", index, temp_path, None))

        # Create or move the highlight to the current index
        grid_manager.highlight_index(app, index)

    if type_ == "MOVE":
        # Retrieve indexes from last action index parameters
        index_a, index_b = index
        move_type = last_action[3]

        # Initialize temp path
        temp_path = None

        if move_type == "SWITCH":
            item_a = images[index_a]
            item_b = images[index_b]

            origin_a = maths.cell_origin(index_a)
            origin_b = maths.cell_origin(index_b)

            if item_a:
                item_a.setPos(*origin_b)
                images[index_b] = item_a

            if item_b:
                item_b.setPos(*origin_a)
                images[index_a] = item_b

            # Add the action back into the undo list
            undo.append(("MOVE", index, None, move_type))

        elif move_type == "OVERWRITE":
            # If "overwrite", remove the image at index_b
            temp_path = grid_manager.remove_from_grid(app, index_b)

            item = images[index_a]
            item.setPos(*maths.cell_origin(index_b))
            images[index_b] = item
            del images[index_a]

            # Add the action back into the undo list
            undo.append(("MOVE", index, temp_path, move_type))

        # Create or move the highlight to the current index
        grid_manager.highlight_index(app, index_b)

    elif type_ == "OVERHAUL":
        # Create temporary files from the main scene
        temp_path = files.create_temp_all(app)

        # Open the previous image again
        if temp:
            grid_manager.load(app, QImage(temp), False, True)
        else:
            grid_manager.clear_main_view(app)

        # Add the action back to the undo list
        undo.append(("OVERHAUL", None, temp_path, None))
