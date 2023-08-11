#!/usr/bin/env python
"""holder.py"""
import sys
import textwrap
import os
import imagehash
from functools import partial
from PySide6.QtCore import QPoint, Qt, QThread, Signal
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFileDialog, QGraphicsPixmapItem, QHeaderView, QTreeWidgetItem, QTreeWidget,
    QVBoxLayout, QDialog, QCheckBox, QGridLayout, QPushButton, QComboBox, QLabel)
from PIL import Image
from classes.frame import FloatingFrame
from modules import files
from modules import grid_manager
from modules import maths
from modules import utils


def holder_presets(app, preset):
    if preset == "SV Actor | 192x160":
        utils.config_changes_restart(
            app, "Type", "SV Actor", "Holder", "192x160")
    if preset == "SV Actor | 160x160":
        utils.config_changes_restart(
            app, "Type", "SV Actor", "Holder", "160x160")


def format_current_grid_to_mz(app):
    # Get the file path to save the image
    file_path, _ = QFileDialog.getSaveFileName(
        None, "Save File", "", "PNG Files(*.png)")

    if not file_path:
        return

    # Hard mapping indexes
    index_list = [
        (1, 0), (2, 0), (3, 0), (1, 4), (2, 4), (3, 4), (1, 9), (2, 9), (3, 9),
        (1, 7), (2, 7), (3, 7), (1, 5), (2, 5), (3, 5), (1, 10), (2, 10), (3, 10),
        (1, 7), (2, 7), (3, 7), (1, 6), (2, 6), (3, 6), (1, 2), (2, 2), (3, 2),
        (1, 1), (2, 1), (3, 1), (1, 11), (2, 11), (3, 11), (1, 2), (2, 2), (3, 2),
        (1, 3), (2, 3), (3, 3), (1, 10), (2, 10), (3, 10), (1, 2), (2, 2), (3, 2),
        (1, 1), (2, 1), (3, 1), (1, 5), (2, 5), (3, 5), (1, 12), (2, 12), (3, 12)
    ]

    # Retrieve cell size from the app
    cell_width, cell_height = app.cell_size

    # Create a new pixmap that fit mz format
    pixmap = QPixmap(9 * cell_width, 6 * cell_height)
    pixmap.fill(Qt.GlobalColor.transparent)

    # Draw each item at the corresponding index to the pixmap
    painter = QPainter(pixmap)
    col, row = 0, 0

    for index, item in enumerate(index_list):
        cell_origin = maths.cell_origin((col, row))
        image = grid_manager.get_image_at(app, item)
        if not image:
            continue
        painter.drawPixmap(*cell_origin, image.pixmap())

        col += 1

        if (index + 1) % 9 == 0:
            row += 1
            col = 0

    painter.end()
    pixmap.save(file_path)


def format_folder_to_mz(app):
    # Prompt for a folder with image
    directory, images = files.prompt_folder(app)

    if not images:
        return

    # Prompt for a folder to save file
    folder_path = QFileDialog.getExistingDirectory(
        None, "Select Output Folder", "/")

    if not folder_path:
        return

    # Display the progress bar
    app.progress_bar.move(
        app.width() // 2 - app.progress_bar.width() // 2,
        app.height() // 2 - app.progress_bar.height() // 2)
    app.progress_bar.setVisible(True)

    current_value = 0

    for index, filename in enumerate(images):
        # Keep track of the methods progress
        current_value += 1
        progress = current_value / len(images) * 100
        app.progress_bar.setValue(progress)

        # Remove the progress bar if the methods reached the end
        if progress >= 100:
            app.progress_bar.move(app.width(), app.height())
            app.progress_bar.setVisible(False)
            app.progress_bar.setValue(0)

        image_path = directory.absoluteFilePath(filename)

        image = QImage(image_path)

        if image.height() == 2240:
            cell_height = 160
        elif image.height() == 2688:
            cell_height = 192
        else:
            continue

        if image.width() == 640:
            cell_width = 160
        elif image.width() == 768:
            cell_width = 192
        else:
            continue

        # Hard mapping indexes
        index_list = [
            (1, 0), (2, 0), (3, 0), (1, 4),
            (2, 4), (3, 4), (1, 9), (2, 9),
            (3, 9), (1, 7), (2, 7), (3, 7),
            (1, 5), (2, 5), (3, 5), (1, 10),
            (2, 10), (3, 10), (1, 7), (2, 7),
            (3, 7), (1, 6), (2, 6), (3, 6),
            (1, 2), (2, 2), (3, 2), (1, 1),
            (2, 1), (3, 1), (1, 11), (2, 11),
            (3, 11), (1, 2), (2, 2), (3, 2),
            (1, 3), (2, 3), (3, 3), (1, 10),
            (2, 10), (3, 10), (1, 2), (2, 2),
            (3, 2), (1, 1), (2, 1), (3, 1),
            (1, 5), (2, 5), (3, 5), (1, 12),
            (2, 12), (3, 12)
        ]

        # Create a new pixmap that fit mz format
        pixmap = QPixmap(9 * cell_width, 6 * cell_height)
        pixmap.fill(Qt.GlobalColor.transparent)

        # Draw each item at the corresponding index to the pixmap
        painter = QPainter(pixmap)
        col, row = 0, 0

        for index, item in enumerate(index_list):
            cell_origin = (col * cell_width, row * cell_height)
            item_origin = (item[0] * cell_width, item[1] * cell_height)
            copied_image = image.copy(
                *item_origin, cell_width, cell_height)
            painter.drawPixmap(
                *cell_origin, QPixmap.fromImage(copied_image))

            col += 1

            if (index + 1) % 9 == 0:
                row += 1
                col = 0

        painter.end()

        image_path = os.path.join(
            folder_path, f"{filename}_[MZ_Format].png")

        pixmap.save(image_path)


def add_weapon_layer(app, file_path, layer):
    image = QImage(file_path)

    if not image:
        return

    cell_width, cell_height = app.cell_size

    # Display the progress bar
    max_value = maths.grid_col() * max(min(
        image.height() // cell_height, maths.grid_row()), 1)
    app.progress_bar.move(
        app.width() // 2 - app.progress_bar.width() // 2,
        app.height() // 2 - app.progress_bar.height() // 2
    )
    app.progress_bar.setVisible(True)
    current_value = 0

    if app.weapons:
        for item in app.weapons:
            app.main_view.scene.removeItem(
                grid_manager.get_weapons(app, item)[0])

    app.weapons.clear()

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
                app.progress_bar.move(app.width(), app.height())
                app.progress_bar.setVisible(False)
                app.progress_bar.setValue(0)

            # Skip "empty" image
            if not utils.has_valid_pixel(crop_image):
                continue

            # Calculate the grid cell origin
            cell_index = (column, row)
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

            # Create a pixmap item and set its position
            pixmap_item = QGraphicsPixmapItem(pixmap)
            pixmap_item.setPos(*cell_origin)

            if layer == "below":
                pixmap_item.setZValue(-2)
                layer = -2
            else:
                pixmap_item.setZValue(2)
                layer = 2

            # Adds it to the main scene and app dict
            app.main_view.scene.addItem(pixmap_item)
            app.weapons[cell_index] = (pixmap_item, layer)


def remove_weapon_layer(app):
    if not app.weapons:
        return

    # Loop through all item and save them
    for item in app.main_view.scene.items():
        if isinstance(item, QGraphicsPixmapItem):
            for values in app.weapons.values():
                if item == values[0]:
                    app.main_view.scene.removeItem(item)

    app.weapons.clear()


def save_chara_with_weapon(app):
    if not app.images or not app.weapons:
        return

    # Get the file path to save the image
    file_path, _ = QFileDialog.getSaveFileName(
        None, "Save File", "", "PNG Files (*.png)")

    if file_path:
        # Retrieve cell width and height from the app
        cell_width, cell_height = app.cell_size
        width = maths.grid_col() * cell_width
        height = maths.grid_row() * cell_height

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

            # Get all items in the scene sorted by ZValue
            items = sorted(
                app.main_view.scene.items(), key=lambda item: item.zValue())

            # Draw the items to the pixmap
            for item in items:
                if isinstance(item, QGraphicsPixmapItem):
                    painter.drawPixmap(
                        QPoint(int(item.pos().x()), int(item.pos().y())),
                        item.pixmap()
                    )

        painter.end()

        # Save the pixmap as an image file
        pixmap.save(file_path)


def pixel_comparaison(image):
    """
    Compare the given image to characters
    """
    # Characters image loading
    if getattr(sys, 'frozen', False):
        parent_folder = sys._MEIPASS
    else:
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.abspath(
            os.path.join(current_path, "../.."))
    image_path = os.path.join(parent_folder, "res", "characters.png")
    characters = Image.open(image_path)
    # Define the letters directory
    letters = {
        "a": (0, 0),
        "b": (6, 0),
        "c": (12, 0),
        "d": (18, 0),
        "e": (24, 0),
        "f": (30, 0),
        "g": (36, 0),
        "h": (42, 0),
        "i": (48, 0),
        "j": (54, 0),
        "k": (60, 0),
        "l": (66, 0),
        "m": (72, 0),
        "n": (78, 0),
        "o": (84, 0),
        "p": (0, 6),
        "q": (6, 6),
        "r": (12, 6),
        "s": (18, 6),
        "t": (24, 6),
        "u": (30, 6),
        "v": (36, 6),
        "w": (42, 6),
        "x": (48, 6),
        "y": (54, 6),
        "z": (60, 6),
        ":": (0, 12),
        "(": (6, 12),
        ")": (12, 12),
        "/": (18, 12),
        " ": (24, 12),
        "1": (0, 18),
        "2": (6, 18),
        "3": (12, 18),
        "4": (18, 18),
        "5": (24, 18),
        "7": (36, 18),
        "8": (42, 18),
        "9": (48, 18),
        "0": (54, 18)
    }

    for letter in letters.values():
        character = characters.crop(
            (letter[0], letter[1], letter[0] + 6, letter[1] + 6))

        # Calculate the hashes of the images
        hash1 = imagehash.average_hash(character)
        hash2 = imagehash.average_hash(image)

        # Calculate the similarity between the hashes
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)

        # Returns the letter if the similarity is higher than 80%
        if similarity >= 0.8:
            return utils.get_key_from_value(letters, letter)

        # Else try with the next letter
        continue

    return ""


def actor_classes():
    """
    Compare pixel from the given file_path with the characters.png and
    retrieve the actor classes from it.

    Args:
        - file_path: The path to the image.
    """
    job_selector = JobSelector()
    result = job_selector.exec_()

    if result == QDialog.Accepted:
        classes = job_selector.get_classes()
    else:
        classes = ""

    return classes


def weapon_class(file_path):
    """
    Retrieve the weapon class from the image by comparing with character images

    Args:
        - file_path: The file_path to identify
    """
    if not file_path:
        return

    # Check if the file is an image
    if file_path[-4:] in [".jpg", ".jpeg", ".png", ".gif"]:
        image = Image.open(file_path)

        # Compare retrieve the image size in order to define the inspected region
        image_width, image_height = image.size

        # Skip if the format is not one of "Holder's"
        if not image_height == 2240:
            return ""

        x = 214
        y = image_height - 90

        # Initialize a dictionary to hold identified letters
        identified_letters = []

        # Loop through the image and identify letters
        for x in range(x, x * 2, 6):
            cropped_image = image.crop((x, y, x + 6, y + 6))
            identified_letters.append(pixel_comparaison(cropped_image))

        return "".join(identified_letters)


def weapon_type(string):
    """Retrieve the weapon type from the class"""
    jobs = {
        "acrobat": "Yoyo",
        "archer": "Bow",
        "assist": "Stick",
        "barbarian": "Hammer",
        "fighter": "Knuckle",
        "hunter": "Gun",
        "knight": "2 Handed Sword",
        "lancer": "Spear",
        "mage": "Stave",
        "sage": "Ball",
        "samurai": "Katana",
        "squire": "1 Handed Sword",
        "thief": "Dagger",
        "witch": "Broom",
        "wizard": "Wand",
        "rogue": "Whip",
        "soldier": "Rifle",
        "dancer": "Fan",
        "reaper": "Scythe",
        "cleric": "Mace",
        "ranger": "Crossbow",
        "crusader": "2 Handed Axe",
        "paladin": "Shield",
        "sentinel": "Heavygun",
        "elementor": "Book",
        "assassin": "Dual",
        "mercenary": "1 Handed Axe",
        "fencer": "Rapier",
        "jester": "Ring",
        "psychic": "Mask"
    }

    if string in jobs:
        return jobs[string]

    return ""


def weapon_layer(file_path):
    """
    Retrieve the weapon class from the image by comparing with character images

    Args:
        - file_path: The file_path to identify
    """
    # Check if the file is an image
    if file_path[-4:] in [".jpg", ".jpeg", ".png", ".gif"]:
        image = Image.open(file_path)

        # Compare retrieve the image size in order to define the inspected region
        image_width, image_height = image.size

        # Skip if the format is not one of "Holder's"
        if not image_height == 2240:
            return ""

        x = 196
        y = image_height - 80

        # Initialize a dictionary to hold identified letters
        identified_letters = []

        # Loop through the image and identify letters
        for x in range(x, x * 2, 6):
            cropped_image = image.crop((x, y, x + 6, y + 6))
            identified_letters.append(pixel_comparaison(cropped_image))

        return "".join(identified_letters)


class DataProcessingThread(QThread):
    processed = Signal(dict)

    def __init__(self, label, weapon_folder, actor_classes):
        super().__init__()
        self.label = label
        self.weapon_folder = weapon_folder
        self.actor_classes = actor_classes

    def run(self):
        data = {
            "Recommended": {},
            "Not Recommended": {}
        }

        files_count = len(os.listdir(self.weapon_folder))
        self.label.setText(f"File(s): 0/{files_count}")
        loaded_files = 0

        for filename in os.listdir(self.weapon_folder):
            loaded_files += 1
            self.label.setText(f"File(s): {loaded_files}/{files_count}")
            file_path = os.path.normpath(
                os.path.join(self.weapon_folder, filename))
            if not any(file_path.endswith(ext) for ext in (".png", ".jpg", ".jpeg")):
                continue

            _weapon_class = weapon_class(file_path)
            _weapon_layer = weapon_layer(file_path)

            if _weapon_class:
                _weapon_class = _weapon_class.replace(" ", "")
                _weapon_layer = _weapon_layer.replace(" ", "")
                _weapon_type = weapon_type(_weapon_class)
                if _weapon_class in self.actor_classes:
                    if _weapon_type not in data["Recommended"]:
                        data["Recommended"][_weapon_type] = []
                    data["Recommended"][_weapon_type].append(
                        (os.path.basename(file_path), _weapon_layer, file_path))
                else:
                    if _weapon_type not in data["Not Recommended"]:
                        data["Not Recommended"][_weapon_type] = []
                    data["Not Recommended"][_weapon_type].append(
                        (os.path.basename(file_path), _weapon_layer, file_path))
            else:
                if "Others" not in data["Not Recommended"]:
                    data["Not Recommended"]["Others"] = []
                data["Not Recommended"]["Others"].append(
                    (os.path.basename(file_path), "Undefined", file_path))

        self.processed.emit(data)


def tree_view(app):
    response = utils.show_popup(textwrap.dedent("""
        This action can take a while depending of the number of image in the input
        <br>folder.
        <br>
        <br>If you want to make the process quicker, it's recommended to create
        <br>new folders with fewer images files inside. (~10min / 1000 images)
        <br>
        <br>
        <br>Do you want to continue ?                         
        """), "WARNING", ["OK", "CANCEL"], "Slow Process Warning")
    if response != "OK":
        return

    weapon_folder = files.prompt_folder(app)
    _actor_classes = actor_classes()

    if app.weapon_frame:
        app.removeToolBar(app.weapon_frame)
        app.weapon_frame.deleteLater()
        app.tree_view.deleteLater()

    app.tree_view = QTreeWidget()
    app.tree_view.setFixedHeight(app.height())
    app.tree_view.setColumnCount(1)
    app.tree_view.setHeaderLabels(["Name", "Layer", "Type", "Path"])

    app.tree_view.header().resizeSection(0, 300)
    app.tree_view.header().resizeSection(1, 60)
    app.tree_view.header().resizeSection(2, 30)
    app.tree_view.header().setSectionResizeMode(1, QHeaderView.Fixed)
    app.tree_view.header().setSectionResizeMode(2, QHeaderView.Fixed)

    app.tree_view.setFixedSize(280, 600)

    def update_tree_widget(data, tree_view):
        items = []
        for key in data:
            for sub_key, values in data[key].items():
                item = QTreeWidgetItem([key])
                sub_item = QTreeWidgetItem([sub_key])
                for value in values:
                    file = value[0].split(".")[-2].upper()
                    ext = value[0].split(".")[-1].upper()
                    child = QTreeWidgetItem([file, value[1], ext, value[2]])
                    sub_item.addChild(child)
                    item.addChild(sub_item)
                items.append(item)
            tree_view.insertTopLevelItems(0, items)

    def item_clicked(item, column):
        layer = item.text(1)
        file_path = item.text(3)
        if file_path == "":
            return
        add_weapon_layer(app, file_path, layer)

    button_save = QPushButton("Save Sheet With Weapon")
    button_remove = QPushButton("Remove Weapon From Sheet")
    label = QLabel("0/0 File(s)")

    app.weapon_frame = FloatingFrame()
    app.weapon_frame.setWindowTitle("Weapon Tree View")
    layout = QVBoxLayout()
    app.weapon_frame.setFixedSize(300, app.height())
    layout.addWidget(label)
    layout.addWidget(app.tree_view)
    layout.addWidget(button_save)
    layout.addWidget(button_remove)
    app.weapon_frame.setLayout(layout)
    app.weapon_frame.show()

    button_save.clicked.connect(
        lambda: save_chara_with_weapon(app))
    button_remove.clicked.connect(
        lambda: remove_weapon_layer(app))
    app.tree_view.data_thread = DataProcessingThread(
        label, weapon_folder[0].absolutePath(), _actor_classes)
    app.tree_view.data_thread.processed.connect(
        lambda data: update_tree_widget(data, app.tree_view))
    app.tree_view.data_thread.start()

    app.tree_view.itemClicked.connect(item_clicked)


class JobSelector(QDialog):
    """Create a dialog to choose jobs or weapon."""

    def __init__(self):
        """Initialize the widget"""
        super().__init__()
        self.setWindowTitle("Weapons/Jobs Selector")
        self.setFixedSize(300, 600)

        # Create attributes for easier uses
        self.checkboxes = {}
        self.comboboxes = {}
        self.buttons = {}

        # Create dictionary with our classes presets
        self.main_job = {
            "Acrobat": "Yoyo",
            "Archer": "Bow",
            "Assist": "Stick",
            "Barbarian": "Hammer",
            "Fighter": "Knuckle",
            "Hunter": "Gun",
            "Knight": "2 Handed Sword",
            "Lancer": "Spear",
            "Mage": "Stave",
            "Sage": "Ball",
            "Samurai": "Katana",
            "Squire": "1 Handed Sword",
            "Thief": "Dagger",
            "Witch": "Broom",
            "Wizard": "Wand",
        }

        self.sub_job = {
            "Rogue": "Whip",
            "Soldier": "Rifle",
            "Dancer": "Fan",
            "Reaper": "Scythe",
            "Cleric": "Mace",
            "Ranger": "Crossbow",
            "Crusader": "2 Handed Axe",
            "Paladin": "Shield",
            "Sentinel": "Heavygun",
            "Elementor": "Book",
            "Assassin": "Dual",
            "Mercenary": "1 Handed Axe",
            "Fencer": "Rapier",
            "Jester": "Ring",
            "Psychic": "Mask",
        }

        self.init_ui()

        self.show()

    def init_ui(self):
        # Create the layout for the dialog
        self.layout = QGridLayout()
        self.label = QLabel("Select the actor's job(s) or weapon(s):")

        self.create_combobox()
        self.create_checkbox()
        self.create_buttons()

        self.setLayout(self.layout)

    def create_combobox(self):
        self.comboboxes["Main"] = QComboBox(self)
        self.comboboxes["Main"].addItem("Custom")
        for item in self.main_job:
            self.comboboxes["Main"].addItem(item)
        self.comboboxes["Main"].currentIndexChanged.connect(
            partial(self.combobox_changed, target="MAIN"))

        self.comboboxes["Sub"] = QComboBox(self)
        self.comboboxes["Sub"].addItem("Custom")
        for item in self.sub_job:
            self.comboboxes["Sub"].addItem(item)
        self.comboboxes["Sub"].currentIndexChanged.connect(
            partial(self.combobox_changed, target="SUB"))

        self.layout.addWidget(self.comboboxes["Main"], 1, 0, 1, 1)
        self.layout.addWidget(self.comboboxes["Sub"], 1, 1, 1, 1)

    def create_checkbox(self):
        for key in self.main_job:
            self.checkboxes[key] = QCheckBox(self.main_job[key])
        for key in self.sub_job:
            self.checkboxes[key] = QCheckBox(self.sub_job[key])

        # Place widgets inside of the grid
        for index, item in enumerate(self.main_job):
            self.layout.addWidget(self.checkboxes[item], 2 + index, 0, 1, 1)

        for index, item in enumerate(self.sub_job):
            self.layout.addWidget(self.checkboxes[item], 2 + index, 1, 1, 1)

    def create_buttons(self):
        """Create buttons"""
        self.buttons["OK"] = QPushButton("OK")
        self.buttons["CANCEL"] = QPushButton("CANCEL")

        self.buttons["OK"].clicked.connect(self.button_clicked)
        self.buttons["CANCEL"].clicked.connect(self.button_clicked)

        # Retrieve the last layout's row
        self.last_row = self.layout.rowCount() + 1

        self.layout.addWidget(self.buttons["OK"], self.last_row, 0, 1, 1)
        self.layout.addWidget(self.buttons["CANCEL"], self.last_row, 1, 1, 1)

    def combobox_changed(self, _, target):
        """Check corresponding checkbox when the combobox is changed."""
        if target == "MAIN":
            combo_text = self.comboboxes["Main"].currentText()
            for item in self.main_job:
                self.checkboxes[item].setChecked(False)
                self.checkboxes[item].setEnabled(False)

                if combo_text == "Custom":
                    self.checkboxes[item].setEnabled(True)

            if combo_text in self.main_job:
                self.checkboxes[combo_text].setChecked(True)

        elif target == "SUB":
            combo_text = self.comboboxes["Sub"].currentText()
            for item in self.sub_job:
                self.checkboxes[item].setChecked(False)
                self.checkboxes[item].setEnabled(False)

                if combo_text == "Custom":
                    self.checkboxes[item].setEnabled(True)

            if combo_text in self.sub_job:
                self.checkboxes[combo_text].setChecked(True)

    def button_clicked(self):
        button = self.sender().text()
        if button == "OK":
            self.accept()

        else:
            self.reject()

    def get_classes(self):
        classes = []
        for item in self.checkboxes:
            if self.checkboxes[item].isChecked():
                classes.append(item.lower())

        return classes
