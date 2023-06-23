#!/usr/bin/env python
"""main_window.py"""
import os
import textwrap
from functools import partial
from PySide6.QtCore import QRect, QRectF, QSize, Qt
from PySide6.QtGui import QAction, QActionGroup, QIcon, QPixmap, QTransform
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QLabel, QMainWindow, QProgressBar, QPushButton)
from classes.graphics_view import GraphicsView
from classes.labels import RoundLabel
from classes.sliders_hsv import HueSlider, SaturationSlider, ValueSlider
from classes.sliders_rgb import RedSlider, GreenSlider, BlueSlider
from classes.slider_resize import SliderResize
from classes.slider_rotate import SliderRotate
from modules import config
from modules import image_manipulation
from modules import maths
from modules import misc
from modules import utils


class MainWindow(QMainWindow):
    """
    Main Window class for the application

    This class represents the main window of the application
    and contains methods for initializing the user interface and
    handling various UI elements and actions.
    """

    def __init__(self):
        """Initialize the main window and add properties for later use."""
        super().__init__()

        # Initialize menu bar menus
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.view_menu = self.menu_bar.addMenu("View")
        self.help_menu = self.menu_bar.addMenu("Help")

        # Create actions groups for checkable actions
        self.group_preset = QActionGroup(self)
        self.group_size = QActionGroup(self)
        self.group_tile = QActionGroup(self)

        # Create dict to keep tracks of our widgets across modules
        self.buttons = {}
        self.buttons_anim = {}
        self.buttons_edit = {}
        self.buttons_offs = {}
        self.sliders = {}
        self.labels = {}

        # Initialize more properties that will be used across the app
        self.last_hsv = {"hue": 0, "saturation": 0, "value": 0}
        self.last_rgb = {"red": 0, "green": 0, "blue": 0}
        self.animation = [None, None]
        self.thread_running = False
        self.toolbar = None

        self.images = {}
        self.layer_1 = {}

        self.copied_image = self.modified_image = None
        self.undo = []
        self.redo = []
        self.temp = []
        self.cell_size = maths.cell_size()

        # Initialize main_view, zoom_view & zoom_scene
        self.main_view = GraphicsView(self)
        self.zoom_view = QGraphicsView(self)
        self.zoom_scene = QGraphicsScene(self)

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface.

        This method sets up the main window, creates UI elements,
        and displays the window
        """
        self.setWindowTitle("Set Manager (Version 1.1.1)")
        self.setFixedSize(
            min(1600, 484 + maths.grid_col() * self.cell_size[0]), 800)

        # call UI elements corresponding methods
        self.create_buttons()
        self.create_buttons_anim()
        self.create_buttons_edit()
        self.create_buttons_offs()
        self.create_main_view()
        self.create_zoom_view()
        self.create_progress_bar()
        self.create_menu_bar()
        self.create_sliders()
        self.create_labels()

        # Show the window
        self.show()

        # Ensure that the displayed area is at the top left
        self.main_view.ensureVisible(QRectF(0, 0, 1, 1))

        # Display a warning message about experimental build
        if config.config_get("EXPERIMENTAL-FEATURES") == "Enabled":
            utils.show_popup(textwrap.dedent("""
                    Some features are still in development and can affect this software
                    performances.
                    
                    If you encounter any bugs are issues, please report them using the
                    corresponding buttons inside of the help menu.
                """), "WARNING", ["OK"], "Experimental Features")

            config.config_set("EXPERIMENTAL-FEATURES", "Disabled")

        # Connect buttons and actions to their respectives methods
        misc.connect_buttons(self)
        misc.connect_actions(self)

    def create_buttons(self):
        """Create buttons in the main window."""
        button_x, button_y, button_spacing = 8, 215, 54
        button_items = ["New", "Open", "Add After",
                        "Load Folder", "-", "-", "-",
                        "Save Highlighted Cell",
                        "Save Individually Each Cell",
                        "Save All Together"]

        for item in button_items:
            # Add a gap if item is "-"
            if item == "-":
                button_y += button_spacing
                continue

            # Creates
            self.buttons[item] = QPushButton(item, self)
            self.buttons[item].setGeometry(button_x, button_y, 254, 50)
            button_y += button_spacing

    def create_buttons_anim(self):
        """Create animation buttons in the main window."""
        if (config.config_get("Type")
                in ["Sprites", "SV Actor", "States", "Weapons", "Balloons", "Custom"]):
            button_items = ["Play", "Stop"]
            for item in button_items:
                self.buttons_anim[item] = QPushButton(item, self)
                if item == "Play":
                    self.buttons_anim[item].setGeometry(
                        QRect(54, 193, 80, 20))
                if item == "Stop":
                    self.buttons_anim[item].setGeometry(
                        QRect(134, 193, 80, 20))

    def create_buttons_edit(self):
        """Create edit buttons in the main window."""
        button_x, button_y, button_spacing = self.width() - 184, 28, 140
        button_items = ["Offset", "Rotate", "Flip",
                        "Horizontal", "Vertical",
                        "Resize", "Hue", "Saturation",
                        "Brightness", "Red", "Green", "Blue"]

        for item in button_items:
            # Create buttons
            self.buttons_edit[item] = QPushButton(item, self)

            if item == "Horizontal":
                self.buttons_edit[item].setGeometry(
                    QRect(self.width() - 184, 348, 90, 40))
                continue
            if item == "Vertical":
                self.buttons_edit[item].setGeometry(
                    QRect(self.width() - 94, 348, 90, 40))
                continue

            if item in ["Red", "Green", "Blue"]:
                self.buttons_edit[item].setGeometry(
                    QRect(button_x, button_y + 40, 180, 20))
            else:
                self.buttons_edit[item].setGeometry(
                    QRect(button_x, button_y, 180, 20))

            item_mapping = {
                "Rotate": 160,
                "Flip": 60,
                "Resize": 40
            }

            if item in item_mapping:
                button_spacing = item_mapping[item]

            button_y += button_spacing

    def create_buttons_offs(self):
        """Create offset buttons in the main window."""
        button_items = ["Up", "Right", "Down", "Left"]

        # Retrieve the image which will be used as an icon for the button
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.abspath(os.path.join(current_path, "../.."))
        image_path = os.path.join(parent_folder, "res", "arrow.png")
        offset_icon = QPixmap(image_path)

        for item in button_items:
            # Calculate the middle position of the four buttons
            middle_x, middle_y = self.width() - 114, 88

            # Create buttons
            self.buttons_offs[item] = QPushButton(self)
            self.buttons_offs[item].clicked.connect(
                partial(image_manipulation.offset, self, item))

            # Calculate buttons origin based on the item:
            item_mapping = {
                "Up":    {"dy": -40, "rotation": 0},
                "Right": {"dx": 40, "rotation": 90},
                "Down":  {"dy": 40, "rotation": 180},
                "Left":  {"dx": -40, "rotation": 270}
            }

            if item in item_mapping:
                adjustments = item_mapping[item]
                middle_x += adjustments.get("dx", 0)
                middle_y += adjustments.get("dy", 0)
                rotation = adjustments["rotation"]
            else:
                break

            # Rotate the image icon
            transform = QTransform().rotate(rotation)
            rotated_icon = QIcon(offset_icon.transformed(
                transform, Qt.TransformationMode.SmoothTransformation))
            self.buttons_offs[item].setGeometry(
                QRect(middle_x, middle_y, 40, 40))
            self.buttons_offs[item].setIcon(rotated_icon)
            self.buttons_offs[item].setIconSize(QSize(32, 32))

    def create_main_view(self):
        """Create the main view for the main window."""
        self.main_view.setGeometry(
            QRect(277, 28, min(self.width() - 463, maths.grid_col()
                  * self.cell_size[0] + 20), 723)
        )

        # Set the background color
        color = config.config_get("BACKGROUND-COLOR")
        self.main_view.setStyleSheet(
            f"background-color: {color}; border: 1px solid red;")

        # Disable the horizontal scrollbar
        self.main_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def create_zoom_view(self):
        """Create the zoom view for the main window."""
        if config.config_get("TYPE") == "Weapons":
            self.zoom_view.setGeometry(QRect(14, 28, 240, 160))
            self.zoom_scene.setSceneRect(QRect(0, 0, 240, 160))
        else:
            self.zoom_view.setGeometry(QRect(54, 28, 160, 160))
            self.zoom_scene.setSceneRect(QRect(0, 0, 160, 160))

        # Set the background color
        color = config.config_get("BACKGROUND-COLOR")
        self.zoom_view.setStyleSheet(
            f"background-color: {color}; border: 1px solid red;")

        # Disable both horizontal and vertical scrollbar
        self.zoom_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.zoom_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Attach the zoom scene which will serve to display image
        self.zoom_view.setScene(self.zoom_scene)

    def create_progress_bar(self):
        """
        Create a progress bar that will be displayed in
        case of images loading or saving.
        """
        self.progress_bar = QProgressBar(self)

        # Place it out of bounds as we don't need it yet
        self.progress_bar.setGeometry(
            QRect(self.width(), self.height(), 300, 40))

        self.progress_bar.setVisible(False)

    def create_menu_bar(self):
        """Create the menu actions for the window."""
        # Create menu actions
        self.create_menu_actions(
            self.file_menu, [
                "New", "Open", "-",
                "Save All Together",
                "Save Highlighted Cell",
                "Save Individually Each Cell",
                "-", "Exit"])

        self.create_menu_actions(
            self.edit_menu, ["Undo", "Redo", "-", "Cut", "Copy", "Paste"])

        self.create_menu_actions(
            self.view_menu, ["Theme", "-"])

        self.create_menu_actions(
            self.help_menu, [
                "About", "-", "Contributors", "Supporters", "-", "Report Issue"])

        # Create sub menu actions
        self.preset_menu = self.view_menu.addMenu("Presets")
        if config.config_get("TYPE") == "Tileset":
            self.tile_menu = self.view_menu.addMenu("Tileset Presets")
        self.size_menu = self.view_menu.addMenu("Cell Size")
        self.view_menu.addSeparator()
        self.creator_menu = self.view_menu.addMenu("Creator Compatibility")
        self.holder_menu = self.creator_menu.addMenu("Holder")
        self.view_menu.addSeparator()
        self.create_menu_actions(self.view_menu, ["Custom Grid"])

        # Create checkable actions
        self.create_checkable_actions(self.preset_menu, [
            "Icons", "Tileset", "Faces",
            "SV Actor", "Sprites", "States", "Weapons",
            "Balloons"],
            self.group_preset, "TYPE"
        )

        if config.config_get("TYPE") == "Tileset":
            self.create_checkable_actions(self.tile_menu, [
                "A1-A2", "A3", "A4", "A5", "B-E"],
                self.group_tile, "TILESET SHEET"
            )

        self.create_checkable_actions(self.size_menu, [
            "16x16", "24x24", "32x32", "48x48", "-", "Custom Cell Size"],
            self.group_size, "CELL SIZE"
        )

        self.create_menu_actions(self.holder_menu, [
            "SV Actor | 192x160", "SV Actor | 160x160", "-",
            "Load Weapons Folder", "-",
            "Format Current Sheet to MZ",
            "Format Whole Folder to MZ",
            "-", "Open Holder's itch.io Page"]
        )

        # Set styles for checked items
        self.view_menu.setStyleSheet('''
            QMenu::item:checked { background-color: dark_grey; }
            QMenu::indicator:checked {
                background-color: green; width: 12px; height: 12px;
            }
        ''')

    def create_menu_actions(self, menu, actions):
        """
        Create menu actions from the given list into the given action

        Args:
            - menu (QMenu): The menu to which actions will be added
            - actions (list): A list of action names to create.
        """
        # Create menu actions from the given list
        for action in actions:
            if action == "-":
                menu.addSeparator()
            else:
                menu.addAction(action)
                for _action in menu.actions():
                    if "(WIP)" in _action.text():
                        _action.setEnabled(False)

                    if (config.config_get("CREATOR") != "Holder" and _action.text() in [
                        "Load Weapons Folder", "Format Current Sheet to MZ",
                            "Format Whole Folder to MZ"]):
                        _action.setEnabled(False)

    def create_checkable_actions(self, menu, actions, action_group, config_key):
        """
        Create checkable actions from the given list and add them to the
        menu.

        Args:
            - menu (QMenu): The menu to which the actions will be added.
            - actions (list): A list of actions names to create.
            - action_group (QActionGroup): The action group to which the
                actions will be added.
            - config_key (str): The configuration key associated with the
                actions.
        """
        # Create checkable actions from the given list and add them to the menu
        for action in actions:
            if action == "-":
                menu.addSeparator()
            else:
                action = QAction(action)
                action.setCheckable(True)
                action_group.addAction(action)
                menu.addAction(action)

                if (config.config_get("TYPE") == "Holder SV Actors"
                        and action.text() in [
                            "16x16", "24x24", "32x32", "48x48", "Custom Cell Size"]):
                    action.setEnabled(False)
                    continue

                if (config.config_get("TYPE") != "Tileset"
                        and action.text() in ["A1-A2", "A3", "A4", "A5", "B-E"]):
                    action.setEnabled(False)
                    continue

                if "(WIP)" in action.text():
                    action.setEnabled(False)

                if action.text() == config.config_get(config_key):
                    action.setChecked(True)

    def create_sliders(self):
        """Create slider in the main window."""
        sliders_items = [
            "Rotate", "Resize", "Hue",
            "Saturation", "Value",
            "Red", "Green", "Blue"
        ]

        for item in sliders_items:
            slider_mapping = {
                "Rotate": {
                    "slider_type": SliderRotate,
                    "geometry": QRect(self.width() - 162, 188, 140, 140)
                },
                "Resize": {
                    "slider_type": SliderResize,
                    "geometry": QRect(self.width() - 184, 408, 180, 20)
                },
                "Hue": {
                    "slider_type": HueSlider,
                    "geometry": QRect(self.width() - 184, 448, 180, 20)
                },
                "Saturation": {
                    "slider_type": SaturationSlider,
                    "geometry": QRect(self.width() - 184, 488, 180, 20)
                },
                "Value": {
                    "slider_type": ValueSlider,
                    "geometry": QRect(self.width() - 184, 528, 180, 20)
                },
                "Red": {
                    "slider_type": RedSlider,
                    "geometry": QRect(self.width() - 184, 608, 180, 20)
                },
                "Green": {
                    "slider_type": GreenSlider,
                    "geometry": QRect(self.width() - 184, 648, 180, 20)
                },
                "Blue": {
                    "slider_type": BlueSlider,
                    "geometry": QRect(self.width() - 184, 688, 180, 20)
                }
            }

            if item in slider_mapping:
                slider_info = slider_mapping[item]
                self.sliders[item] = slider_info["slider_type"](self)
                self.sliders[item].setGeometry(slider_info["geometry"])

    def create_labels(self):
        """Create labels in the main window."""
        label_items = ["Type", "Index"]
        for item in label_items:
            self.labels[item] = QLabel(self)
            self.labels[item].setAlignment(Qt.AlignmentFlag.AlignCenter)

            if item == "Type":
                self.labels[item].setGeometry(
                    QRect(0, self.height() - 32, 277, 32))

                if config.config_get("TYPE") == "Tileset":
                    self.labels[item].setText(
                        "Current Settings: ● "
                        + config.config_get("Type") + " ● "
                        + str(self.cell_size[0]) + "x"
                        + str(self.cell_size[1]) + " ● "
                        + config.config_get("Tileset Sheet") + " ●"
                    )
                else:
                    self.labels[item].setText(
                        "Current Settings: ● "
                        + config.config_get("Type") + " ● "
                        + str(self.cell_size[0]) + "x"
                        + str(self.cell_size[1]) + " ●"
                    )

            elif item == "Index":
                self.labels[item].setGeometry(QRect(
                    277,
                    self.height() - 32,
                    min(723, maths.grid_col() * self.cell_size[1] + 20),
                    32
                ))
                self.labels[item].setText(
                    "Select a cell to display the index here")

        # Create the round label for rotate
        self.labels["Rotate"] = RoundLabel(80, 80, self)
        self.labels["Rotate"].setGeometry(
            QRect(self.width() - 133, 216, 80, 80))
        self.labels["Rotate"].setText("0°")
