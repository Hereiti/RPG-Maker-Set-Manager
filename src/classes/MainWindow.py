#================================================================================#
# File: MainWindow.py
# Created Date: 26-05-2023 | 00:41:01
# Author: Hereiti
#================================================================================
# Last Modified: 04-06-2023 | 01:06:04
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Imports
#================================================================================#
import os

#================================================================================#
# Third-Party Imports
#================================================================================#
from PySide6.QtCore import QRect, Qt, QSize, QRectF
from PySide6.QtGui import QAction, QActionGroup, QIcon, QTransform, QPixmap
from PySide6.QtWidgets import QGraphicsView, QMainWindow, QPushButton, QLabel, QSlider, QGraphicsScene

#================================================================================#
# Local Application Imports
#================================================================================#
from classes.GraphicsView import GraphicsView
from classes.Widget import CircularSlider, RoundButton

from modules import config, maths, miscellaneous, edits

#================================================================================#
# Class
#================================================================================#
class MainWindow(QMainWindow):
    """Main window class for the Set Manager application.

    This class represents the main window of the application and contains methods
    for initializing the user interface and handling various UI elements and actions.

    """
    def __init__(self):
        """Initialize the main window and set up the user interface."""
        super().__init__()

        # Menu Bar
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.view_menu = self.menu_bar.addMenu("View")
        self.help_menu = self.menu_bar.addMenu("Help")

        # Widgets
        self.labels = {}
        self.buttons = {}
        self.sliders = {}
        self.edits_buttons = {}
        self.offset_buttons = {}

        # Action Groups
        self.action_group_icon = QActionGroup(self)
        self.action_group_type = QActionGroup(self)
        self.action_group_tileset = QActionGroup(self)

        # Graphics Views
        self.main_view = GraphicsView(self)
        self.zoom_view = QGraphicsView(self)
        self.zoom_scene = QGraphicsScene(self.zoom_view)

        # Properties
        self.cell_size = maths.cell_size()
        self.undo = []
        self.redo = []
        self.icons = {}

        # Temporary
        self.copied_icon = None
        self.modified_icon = None
        self.temp_files = []
        self.log_name = config.exception()

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface.

        This method sets up the main window, creates UI elements, and displays the window.

        """
        self.setWindowTitle("Set Manager (Version 1.0.5)")
        self.setStyleSheet("background-color: #202020")
        self.setFixedSize(484 + maths.grid_col() * self.cell_size, 800)

        # Create UI elements
        self.create_menu_bar()
        self.create_buttons()
        self.create_edits_buttons()
        self.create_offset_buttons()
        self.create_sliders()
        self.create_zoom_view()
        self.create_main_view()
        self.create_labels()

        # Show the main window and ensure the view is visible
        self.show()
        self.main_view.ensureVisible(QRectF(0, 0, 1, 1))

        # Connect buttons and actions
        miscellaneous.connect_buttons(self)
        miscellaneous.connect_actions(self)

    def create_menu_bar(self) -> None:
        """Create the menu actions in the main window."""
        # Create menu actions
        self.create_menu_actions(self.file_menu, ["New", "Open", "-", "Save All", "Save Selected", "Save Separately", "-", "Exit"])
        self.create_menu_actions(self.edit_menu, ["Undo", "Redo", "-", "Cut", "Copy", "Paste"])
        self.create_menu_actions(self.view_menu, ["Theme", "-"])

        # Create checkable actions
        self.create_checkable_actions(self.view_menu, ["Icon Set", "Tileset", "-"], self.action_group_type, "Type")
        self.create_checkable_actions(self.view_menu, ["16x16", "24x24", "32x32", "48x48", "-"], self.action_group_icon, "Cell Size")
        self.create_checkable_actions(self.view_menu, ["A1-A2", "A3", "A4", "A5", "B-E"], self.action_group_tileset, "Tileset")

        # Set styles for checked items
        self.view_menu.setStyleSheet('''
            QMenu::item:checked { background-color: dark_grey; }
            QMenu::indicator:checked { background-color: green; width: 12px; height: 12px; }
        ''')

        self.create_menu_actions(self.help_menu, ["About"])

    def create_menu_actions(self, menu, actions) -> None:
        """Create menu actions from the given list and add them to the menu.

        Args:
            menu (QMenu): The menu to which the actions will be added.
            actions (list): A list of action names to create.

        """
        # Create menu actions from the given list
        for action in actions:
            if action == "-":
                menu.addSeparator()
            else:
                menu.addAction(action)

    def create_checkable_actions(self, menu, actions, action_group, config_key) -> None:
        """Create checkable actions from the given list and add them to the menu.

        Args:
            menu (QMenu): The menu to which the actions will be added.
            actions (list): A list of action names to create.
            action_group (QActionGroup): The action group to which the actions will be added.
            config_key (str): The configuration key associated with the actions.

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

                if config.get_config("Type") != "Tileset" and action.text() in ["A1-A2", "A3", "A4", "A5", "B-E"]:
                    action.setEnabled(False)
                    continue

                if action.text() == config.get_config(config_key):
                    action.setChecked(True)

    def create_buttons(self) -> None:
        """Create the buttons in the main window."""
        button_x, button_y, button_spacing = 8, 195, 54
        button_items = ["New", "Open", "Add After", "Folder", "-", "-", "-", "Save Selected", "Save Separately", "Save All"]
        for item in button_items:
            if item == "-":
                button_y += button_spacing
                continue

            # Create buttons with properties
            self.buttons[item] = QPushButton(item, self)
            self.buttons[item].setObjectName(item.lower())
            self.buttons[item].setGeometry(QRect(button_x, button_y, 254, 50))
            self.buttons[item].setToolTip(item)
            button_y += button_spacing

    def create_edits_buttons(self) -> None:
        """Create the edit buttons in the main window."""
        edits_button_x, edits_button_y, edits_button_spacing = self.width() - 184, 28, 180
        edits_buttons_items = ["Offset", "Rotate", "Resize"]
        for item in edits_buttons_items:
            # Create edit buttons with properties
            self.edits_buttons[item] = QPushButton(item, self)
            self.edits_buttons[item].setObjectName(item.lower())
            self.edits_buttons[item].setGeometry(QRect(edits_button_x, edits_button_y, 180, 20))

            edits_button_y += edits_button_spacing

    def create_offset_buttons(self) -> None:
        """Create the offset buttons in the main window."""
        middle_x, middle_y = self.width() - 114, 108
        offset_button_items = ["Up", "Left", "Down", "Right"]

        # Get the path of the current file
        current_path = os.path.dirname(os.path.abspath(__file__))
        # Access a folder in the parent directory
        parent_folder_path = os.path.abspath(os.path.join(current_path, '..'))
        image_path = os.path.join(parent_folder_path, "image", "Arrow.png")

        offset_icon = QPixmap(image_path)

        for item in offset_button_items:
            # Create offset buttons with properties
            self.offset_buttons[item] = QPushButton(self)
            self.offset_buttons[item].setObjectName(item.lower())

            if item == "Up":
                middle_y -= 40
                rotation = 0
                self.offset_buttons[item].clicked.connect(lambda checked=False, direction="Up": edits.offset(self, direction))
            elif item == "Down":
                middle_y += 40
                rotation = 180
                self.offset_buttons[item].clicked.connect(lambda checked=False, direction="Down": edits.offset(self, direction))
            elif item == "Right":
                middle_x += 40
                rotation = 90
                self.offset_buttons[item].clicked.connect(lambda checked=False, direction="Right": edits.offset(self, direction))
            elif item == "Left":
                middle_x -= 40
                rotation = 270
                self.offset_buttons[item].clicked.connect(lambda checked=False, direction="Left": edits.offset(self, direction))

            # Rotate the icon
            transform = QTransform().rotate(rotation)
            rotated_icon_image = offset_icon.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            rotated_icon = QIcon(rotated_icon_image)

            self.offset_buttons[item].setGeometry(QRect(middle_x, middle_y, 40, 40))
            self.offset_buttons[item].setIcon(rotated_icon)
            self.offset_buttons[item].setIconSize(QSize(32, 32))

            middle_x, middle_y = self.width() - 114, 108

    def create_sliders(self) -> None:
        """Create the sliders in the main window."""
        slider_items = ["Rotate", "Resize"]
        for item in slider_items:
            if item == "Rotate":
                # Create circular slider for rotation
                self.sliders[item] = CircularSlider(self)
                self.sliders[item].setGeometry(QRect(self.width() - 162, 238, 140, 140))
            elif item == "Resize":
                # Create horizontal slider for resizing
                self.sliders[item] = QSlider(Qt.Orientation.Horizontal, self)
                self.sliders[item].setGeometry(QRect(self.width() - 184, 438, 180, 20))
                self.sliders[item].setMinimum(0)
                self.sliders[item].setMaximum(200)
                self.sliders[item].setValue(100)
                self.sliders[item].valueChanged.connect(lambda value: edits.resize_image(self, value))
                self.sliders[item].sliderReleased.connect(lambda: edits.on_slider_end(self))

            self.sliders[item].setObjectName(item.lower())
            self.sliders[item].setEnabled(False)

    def create_zoom_view(self) -> None:
        """Create the zoom view in the main window."""
        # Create zoom view for magnified display
        color = config.get_config("background-color")
        self.zoom_view.setGeometry(QRect(54, 28, 160, 160))
        self.zoom_view.setStyleSheet(f"background-color: {color}; border: 1px solid red;")
        self.zoom_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.zoom_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.zoom_scene.setSceneRect(QRectF(0, 0, 160, 160))
        self.zoom_view.setScene(self.zoom_scene)

    def create_main_view(self) -> None:
        """Create the main view in the main window."""
        # Create main view for displaying graphics
        color = config.get_config("background-color")
        self.main_view.setGeometry(QRect(277, 28, maths.grid_col() * self.cell_size + 20, 710))
        self.main_view.setStyleSheet(f"QGraphicsView {{ background-color: {color}; border: 1px solid red; }}")
        self.main_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def create_labels(self) -> None:
        """Create the labels in the main window."""
        label_items = ["Type", "Index"]
        for item in label_items:
            self.labels[item] = QLabel(self)
            self.labels[item].setObjectName(item.lower())
            self.labels[item].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.labels[item].setText(item)

            if item == "Type":
                self.labels[item].setGeometry(QRect(0, self.height() - 32, 277, 32))

                if config.get_config("Type") == "Tileset":
                    self.labels[item].setText("Current Settings: ● " + config.get_config("Type") + " ● " + str(maths.cell_size()) + "x" + str(maths.cell_size()) + " ● " + config.get_config("Tileset") + " ●")
                else:
                    self.labels[item].setText("Current Settings: ● " + config.get_config("Type") + " ● " + str(maths.cell_size()) + "x" + str(maths.cell_size()) + " ●")

            elif item == "Index":
                self.labels[item].setGeometry(QRect(277, self.height() - 32, maths.grid_col() * self.cell_size + 20, 32))
                self.labels[item].setText("Select a cell to display the index here")

        _x, _y = self.width() - 180, 418
        label_items = ["ResizeMin", "ResizeValue", "ResizeMax"]
        for item in label_items:
            self.labels[item] = QLabel(self)
            self.labels[item].setObjectName(item.lower())
            self.labels[item].setGeometry(QRect(_x, _y, 60, 20))

            if item == "ResizeMin":
                text = "0%"
                self.labels[item].setAlignment(Qt.AlignmentFlag.AlignLeft)
            elif item == "ResizeValue":
                text = "100%"
                self.labels[item].setAlignment(Qt.AlignmentFlag.AlignHCenter)
            elif item == "ResizeMax":
                text = "200%"
                self.labels[item].setAlignment(Qt.AlignmentFlag.AlignRight)

            self.labels[item].setText(text)
            _x += 60

        # Create round button for rotation value display
        self.buttons["Rotate"] = RoundButton(80, 80, self)
        self.buttons["Rotate"].setGeometry(QRect(self.width() - 133, 266, 80, 80))
        self.buttons["Rotate"].setText("0°")
