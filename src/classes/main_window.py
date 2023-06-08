#================================================================================#
# File: main_window.py
# Created Date: 04-06-2023 | 18:51:19
# Author: Hereiti
#================================================================================
# Last Modified: 08-06-2023 | 13:54:42
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
import os

from functools import partial
from typing import List

#================================================================================#
# Third-party imports
#================================================================================#
from PySide6.QtCore import QRect, QRectF, QSize, Qt
from PySide6.QtGui import QAction, QActionGroup, QIcon, QPixmap, QTransform
from PySide6.QtWidgets import  QGraphicsScene, QGraphicsView, QLabel, QMainWindow, QMenu, QPushButton, QProgressBar, QSlider

#================================================================================#
# Local imports
#================================================================================#
from classes.graphics_view import GraphicsView
from classes.widgets import BrightnessSlider, HueSlider, ResizeSlider, RotateSlider, RoundLabel, SaturationSlider, RedSlider, GreenSlider, BlueSlider

from modules import config
from modules import edits
from modules import maths
from modules import misc

from modules.utils import show_popup

#================================================================================#
# Class
#================================================================================#
class MainWindow(QMainWindow):
    """
    Main window class for the application.
    
    This class represents the main window of the application and
    contains methods for initializing the user interface and handling
    various UI elements and actions.
    """
    def __init__(self) -> None:
        """Initialize the main window and add properties for later use."""
        super().__init__()

        # Initialize menu bar menus
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.view_menu = self.menu_bar.addMenu("View")
        self.help_menu = self.menu_bar.addMenu("Help")

        # Create actions groups for checkable actions
        self.group_type = QActionGroup(self)
        self.group_size = QActionGroup(self)
        self.group_tile = QActionGroup(self)
        self.group_creator = QActionGroup(self)

        # Initialize widget dict for later retrieval
        self.labels = {}
        self.buttons = {}
        self.sliders = {}
        self.edits_buttons = {}
        self.offset_buttons = {}
        self.animation_buttons = {}

        # Initialize more properties that will be used across the app
        self.last_hue = 0
        self.last_saturation = 0
        self.last_brightness = 0
        self.last_color = {"red": 0, "green": 0, "blue": 0}
        self.thread_running = False
        self.animation = [None, None]

        self.undo = []
        self.redo = []
        self.temp = []
        self.images = {}
        self.copied_img = None
        self.modified_img = None
        self.log_name = config.exception()
        self.cell_size = maths.cell_size()

        # Initialize main_view, zoom_view & zoom_scene
        self.main_view = GraphicsView(self)
        self.zoom_view = QGraphicsView(self)
        self.zoom_scene = QGraphicsScene(self)

        self.init_ui()

    def init_ui(self) -> None:
        """
        Initialize the user interface.
        
        This method sets up the main window, creates UI elements,
        and displays the window
        """
        self.setWindowTitle("Set Manager (Version 1.1.0)")
        self.setFixedSize(484 + maths.grid_col() * self.cell_size, 800)

        # call UI elements corresponding methods
        self.create_menu_bar()
        self.create_buttons()
        self.create_edits_buttons()
        self.create_flip_buttons()
        self.create_offset_buttons()
        self.create_animation_buttons()
        self.create_sliders()
        self.create_zoom_view()
        self.create_main_view()
        self.create_labels()
        self.create_progress_bar()

        # Show the main window
        self.show()
        # Ensure that the displayed area is at the top left
        self.main_view.ensureVisible(QRectF(0, 0, 1, 1))

        if config.config_get("experimental-features") == "Enabled":
            show_popup("Some features are still in developement and can affect this app performances.\n\nIf you encounter any bugs are issues, please report them using the\ncorresponding button inside of the help menu.", "WARNING", ["OK"], "Experimental Features")
            config.config_set("experimental-features", "Disabled")

        misc.connect_buttons(self)
        misc.connect_actions(self)

    def create_menu_bar(self) -> None:
        """Create the menu actions for the window."""
        # Create menu actions
        self.create_menu_actions(self.file_menu, ["New", "Open", "-", "Save All Together", "Save Highlighted Cell", "Save Individually Each Cell", "-", "Exit"])
        self.create_menu_actions(self.edit_menu, ["Undo", "Redo", "-", "Cut", "Copy", "Paste"])
        self.create_menu_actions(self.view_menu, ["Theme", "-"])
        self.create_menu_actions(self.help_menu, ["About", "Credits", "-", "Report Issue"])

        # Create sub menu actions
        self.type_menu = self.view_menu.addMenu("Type")
        self.size_menu = self.view_menu.addMenu("Size")
        self.tile_menu = self.view_menu.addMenu("Tileset")
        self.view_menu.addSeparator()
        self.creator_menu = self.view_menu.addMenu("Creator Compatibility (WIP)")
        self.view_menu.addSeparator()
        self.create_menu_actions(self.view_menu, ["Custom Grid (WIP)"])

        # Create checkable actions
        self.create_checkable_actions(self.type_menu, ["Icons", "Tileset", "Faces", "SV Actor", "Sprites"], self.group_type, "TYPE")
        self.create_checkable_actions(self.size_menu, ["16x16", "24x24", "32x32", "48x48", "-", "Custom Size (WIP)"], self.group_size, "CELL SIZE")
        self.create_checkable_actions(self.tile_menu, ["A1-A2", "A3", "A4", "A5", "B-E"], self.group_tile, "TILESET SHEET")
        self.create_checkable_actions(self.creator_menu, ["None"], self.group_creator, "CREATOR COMPATIBILITY")

        # Set styles for checked items
        self.view_menu.setStyleSheet('''
            QMenu::item:checked { background-color: dark_grey; }
            QMenu::indicator:checked { background-color: green; width: 12px; height: 12px; }
        ''')

    def create_menu_actions(self, menu: QMenu, actions: List[str]) -> None:
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

    def create_checkable_actions(self, menu: QMenu, actions: List[str], action_group: QActionGroup, config_key: str) -> None:
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

                if config.config_get("TYPE") == "Faces" and action.text() in ["16x16", "24x24", "32x32", "48x48"]:
                    action.setEnabled(False)
                    continue

                if config.config_get("TYPE") != "Tileset" and action.text() in ["A1-A2", "A3", "A4", "A5", "B-E"]:
                    action.setEnabled(False)
                    continue

                if "(WIP)" in action.text():
                    action.setEnabled(False)

                if action.text() == config.config_get(config_key):
                    action.setChecked(True)

    def create_buttons(self) -> None:
        """Create buttons in the main window."""
        button_x, button_y, button_spacing = 8, 215, 54
        button_items = ["New", "Open", "Add After", "Folder", "-", "-", "-", "Save Highlighted Cell", "Save Individually Each Cell", "Save All Together"]
        for item in button_items:
            if item == "-":
                button_y += button_spacing
                continue

            # Create buttons
            self.buttons[item] = QPushButton(item, self)
            self.buttons[item].setGeometry(QRect(button_x, button_y, 254, 50))
            button_y += button_spacing

    def create_edits_buttons(self) -> None:
        """Create edit buttons in the main window."""
        edits_button_x, edits_button_y, edits_button_spacing = self.width() - 184, 28, 140
        edits_button_items = ["Offset", "Rotate", "Flip", "Resize", "Hue", "Saturation", "Brightness", "Red", "Green", "Blue"]
        for item in edits_button_items:
            # Create buttons
            self.edits_buttons[item] = QPushButton(item, self)
            if item in ["Red", "Green", "Blue"]:
                self.edits_buttons[item].setGeometry(QRect(edits_button_x, edits_button_y + 40, 180, 20))
            else:
                self.edits_buttons[item].setGeometry(QRect(edits_button_x, edits_button_y, 180, 20))
            if item == "Rotate":
                edits_button_spacing = 160
            if item == "Flip":
                edits_button_spacing = 60
            if item == "Resize":
                edits_button_spacing = 40
            edits_button_y += edits_button_spacing

    def create_offset_buttons(self) -> None:
        """Create offset buttons in the main window."""
        offset_button_items = ["Up", "Right", "Down", "Left"]

        # Retrieve the image which will be in the button
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.abspath(os.path.join(current_path, ".."))
        image_path = os.path.join(parent_folder, "image", "Arrow.png")

        offset_icon = QPixmap(image_path)

        for item in offset_button_items:
            # Calculate the middle position of the four buttons
            middle_x, middle_y = self.width() - 114, 88
            # Create offset buttons
            self.offset_buttons[item] = QPushButton(self)
            self.offset_buttons[item].clicked.connect(partial(edits.offset, self, item))

            # Calculate buttons coords
            if item == "Up":
                middle_y -= 40
                rotation = 0
            elif item == "Right":
                middle_x += 40
                rotation = 90
            elif item == "Down":
                middle_y += 40
                rotation = 180
            elif item == "Left":
                middle_x -= 40
                rotation = 270
            else:
                break

            # Rotate the icon
            transform = QTransform().rotate(rotation)
            rotated_icon_image = offset_icon.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            rotated_icon = QIcon(rotated_icon_image)

            self.offset_buttons[item].setGeometry(QRect(middle_x, middle_y, 40, 40))
            self.offset_buttons[item].setIcon(rotated_icon)
            self.offset_buttons[item].setIconSize(QSize(32, 32))

    def create_flip_buttons(self) -> None:
        flip_button_items = ["Horizontal", "Vertical"]
        for item in flip_button_items:
            self.edits_buttons[item] = QPushButton(item, self)

            if item == "Horizontal":
                self.edits_buttons[item].setGeometry(QRect(self.width() - 184, 348, 90, 40))
            if item == "Vertical":
                self.edits_buttons[item].setGeometry(QRect(self.width() - 94, 348, 90, 40))

            self.edits_buttons[item].clicked.connect(partial(edits.flip_image, self, item))

    def create_animation_buttons(self) -> None:
        """Create buttons in the main window."""
        if config.config_get("Type") in ["Sprites", "SV Actor"]:
            animation_button_items = ["Play", "Stop"]
            for item in animation_button_items:
                self.animation_buttons[item] = QPushButton(item, self)
                if item == "Play":
                    self.animation_buttons[item].setGeometry(QRect(54, 193, 80, 20))
                if item == "Stop":
                    self.animation_buttons[item].setGeometry(QRect(134, 193, 80, 20))

    def create_sliders(self) -> None:
        """Create slider in the main window."""
        slider_items = ["Rotate", "Resize", "Hue", "Saturation", "Brightness", "R", "G", "B"]
        for item in slider_items:
            if item == "Rotate":
                # Create a circular slider
                self.sliders[item] = RotateSlider(self)
                self.sliders[item].setGeometry(QRect(self.width() - 162, 188, 140, 140))
            if item == "Resize":
                # Create the resize slider
                self.sliders[item] = ResizeSlider(self)
                self.sliders[item].setGeometry(QRect(self.width() - 184, 408, 180, 20))
            if item == "Hue":
                # Create the hue slider
                self.sliders[item] = HueSlider(self)
                self.sliders[item].setGeometry(QRect(self.width() - 184, 448, 180, 20))
            if item == "Saturation":
                # Create the saturation slider
                self.sliders[item] = SaturationSlider(self)
                self.sliders[item].setGeometry(QRect(self.width() - 184, 488, 180, 20))
            if item == "Brightness":
                # Create the brightness slider
                self.sliders[item] = BrightnessSlider(self)
                self.sliders[item].setGeometry(QRect(self.width() - 184, 528, 180, 20))
            if item == "R":
                # Create the brightness slider
                self.sliders[item] = RedSlider(self)
                self.sliders[item].setGeometry(QRect(self.width() - 184, 608, 180, 20))
            if item == "G":
                # Create the brightness slider
                self.sliders[item] = GreenSlider(self)
                self.sliders[item].setGeometry(QRect(self.width() - 184, 648, 180, 20))
            if item == "B":
                # Create the brightness slider
                self.sliders[item] = BlueSlider(self)
                self.sliders[item].setGeometry(QRect(self.width() - 184, 688, 180, 20))

    def create_zoom_view(self) -> None:
        """Create the zoom view for the main window."""
        self.zoom_view.setGeometry(QRect(54, 28, 160, 160))

        color = config.config_get("BACKGROUND-COLOR")
        self.zoom_view.setStyleSheet(f"background-color: {color}; border: 1px solid red;")

        self.zoom_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.zoom_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.zoom_scene.setSceneRect(QRectF(0, 0, 160, 160))
        self.zoom_view.setScene(self.zoom_scene)

    def create_main_view(self) -> None:
        """Create the main view for the main window."""
        self.main_view.setGeometry(QRect(277, 28, maths.grid_col() * self.cell_size + 20, 723))

        color = config.config_get("BACKGROUND-COLOR")
        self.main_view.setStyleSheet(f"background-color: {color}; border: 1px solid red;")

        self.main_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def create_labels(self) -> None:
        label_items = ["Type", "Index"]
        for item in label_items:
            self.labels[item] = QLabel(self)
            self.labels[item].setAlignment(Qt.AlignmentFlag.AlignCenter)

            if item == "Type":
                self.labels[item].setGeometry(QRect(0, self.height() - 32, 277, 32))

                if config.config_get("TYPE") == "Tileset":
                    self.labels[item].setText("Current Settings: ● " + config.config_get("Type") + " ● " + str(maths.cell_size()) + "x" + str(maths.cell_size()) + " ● " + config.config_get("Tileset Sheet") + " ●")
                else:
                    self.labels[item].setText("Current Settings: ● " + config.config_get("Type") + " ● " + str(maths.cell_size()) + "x" + str(maths.cell_size()) + " ●")

            elif item == "Index":
                self.labels[item].setGeometry(QRect(277, self.height() - 32, maths.grid_col() * self.cell_size + 20, 32))
                self.labels[item].setText("Select a cell to display the index here")

        # Create the round label for rotate
        self.labels["Rotate"] = RoundLabel(80, 80, self)
        self.labels["Rotate"].setGeometry(QRect(self.width() - 133, 216, 80, 80))
        self.labels["Rotate"].setText("0°")

    def create_progress_bar(self) -> None:
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(QRect(self.width(), self.height(), 300, 40))
        self.progress_bar.setVisible(False)
