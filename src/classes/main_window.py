#!/usr/bin/env python
"""main_window.py"""
import os
import sys
import textwrap
import markdown
from functools import partial
from dotenv import load_dotenv
from PySide6.QtCore import QRectF, QSize, Qt, QEvent
from PySide6.QtGui import QAction, QActionGroup, QIcon, QPixmap, QTransform, QCursor
from PySide6.QtWidgets import (
    QGraphicsScene, QLabel, QMainWindow, QProgressBar, QPushButton,
    QTextBrowser, QWidget, QToolBar, QToolTip,
    QStatusBar, QGridLayout, QHBoxLayout, QApplication,
    QLineEdit, QFrame)
from classes.graphics_view import GraphicsView, ZoomView
from classes.sliders_hsv import HueSlider, SaturationSlider, ValueSlider
from classes.sliders_rgb import RedSlider, GreenSlider, BlueSlider
from classes.slider_resize import SliderResize
from classes.slider_rotate import SliderRotate
from classes.frame import FloatingFrame
from modules import config
from modules import image_manipulation
from modules import maths
from modules import misc
from modules import utils

load_dotenv()


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

        # Initialize the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        self.sub_layout = QGridLayout()

        # Initialize menu bar menus
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.view_menu = self.menu_bar.addMenu("View")
        self.help_menu = self.menu_bar.addMenu("Help")
        self.creator_menus = {}
        self.sub_menus = {}

        # Initialize toolbars
        self.toolbar = QToolBar(self)
        self.adjustment_toolbar = QToolBar(self)
        self.toolbar_actions = {}
        self.adjustment_toolbar_actions = {}

        self.toolbars = [self.toolbar, self.adjustment_toolbar]

        self.weapon_frame = None

        # Initialize the status bar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

        # Create actions groups for checkable actions
        self.group_preset = QActionGroup(self)
        self.group_size = QActionGroup(self)
        self.group_tile = QActionGroup(self)

        # Create dicts to have easy references to our widgets across modules
        self.buttons = {}
        self.sliders = {}
        self.frames = {}
        self.labels = {}
        self.values = {}

        # Initialize properties that will serve for most methods
        self.thread_running = False

        self.modified_images = []
        self.copied_images = []
        self.animation = [None, None]
        self.undo = []
        self.redo = []
        self.temp = []

        self.weapons = {}
        self.images = {}

        self.cell_size = maths.cell_size()

        # Initialize main_view, zoom_view, zoom_scene
        self.main_view = GraphicsView(self.central_widget)
        self.zoom_view = ZoomView(self.central_widget)
        self.zoom_scene = QGraphicsScene()
        self.zoom_view.setScene(self.zoom_scene)

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface.

        This method sets up the main window, creates UI elements,
        and displays the window.
        """
        self.setWindowTitle(f"Set Manager (Version {os.getenv('VERSION')})")
        self.setMinimumSize(420 + maths.grid_col() * self.cell_size[0], 600)

        # Call UI elements corresponding methods
        self.create_menu_bar()
        self.create_toolbar()
        self.create_floatingframe()
        self.create_buttons()
        self.create_sliders()
        self.create_labels()
        self.create_views()
        self.create_progress_bar()

        # Display the window
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

        QApplication.instance().installEventFilter(self)

    def create_menu_bar(self):
        """Create the menu actions for the window."""
        # Create menu actions
        menus = {
            self.file_menu: [
                "New", "Open", "-", "Save All Together", "Save Highlighted Cell",
                "Save Individually Each Cell", "-", "Exit"],

            self.edit_menu: ["Undo", "Redo", "-", "Cut", "Copy", "Paste"],
            self.view_menu: ["Theme", "-"],
            self.help_menu: [
                "Report Issue", "-", "Check for Update...", "Releases Notes", "-",
                "Contributors", "Supporters", "-", "About"]
        }

        for menu, actions in menus.items():
            for action in actions:
                if action == "-":
                    menu.addSeparator()
                else:
                    menu.addAction(action)

        # Create sub menu
        sub_menus = {
            self.view_menu: [
                "Presets", "Tilesets", "Cell Size", "-", "Creator Compatibility",
                "-", "Custom Grid"]
        }

        for menu, submenus in sub_menus.items():
            for submenu in submenus:
                if submenu == "-":
                    menu.addSeparator()
                elif submenu == "Custom Grid":
                    menu.addAction(submenu)
                else:
                    self.sub_menus[submenu] = menu.addMenu(submenu)

        checkable_actions = {
            self.sub_menus["Presets"]: {
                self.group_preset:  [
                    "Icons", "Tileset", "Faces", "SV Actor", "Sprites", "States",
                    "Weapons", "Balloons"]
            },

            self.sub_menus["Tilesets"]: {
                self.group_tile: ["A1-A2", "A3", "A4", "A5", "B-E"]
            },

            self.sub_menus["Cell Size"]: {
                self.group_size: [
                    "16x16", "24x24", "32x32", "48x48", "-", "Custom Cell Size"]
            },
        }

        for submenu, values in checkable_actions.items():
            for group, actions in values.items():
                for action in actions:
                    if action == "-":
                        submenu.addSeparator()
                    else:
                        action = QAction(action)
                        action.setCheckable(True)
                        group.addAction(action)
                        submenu.addAction(action)

                        if (config.config_get("TYPE") == "Holder SV Actors"
                            and action.text() in [
                                "16x16", "24x24", "32x32", "48x48",
                                "Custom Cell Size"]):
                            action.setEnabled(False)
                            continue

                        if (config.config_get("TYPE") != "Tileset"
                                and action.text() in [
                                    "A1-A2", "A3", "A4", "A5", "B-E"]):
                            action.setEnabled(False)
                            continue

                        if "(WIP)" in action.text():
                            action.setEnabled(False)

                        if group == self.group_size:
                            config_key = "CELL SIZE"
                        elif group == self.group_tile:
                            config_key = "TILESET SHEET"
                        elif group == self.group_preset:
                            config_key = "TYPE"

                        if action.text() == config.config_get(config_key):
                            action.setChecked(True)

        creator_menus = {
            "Holder": [
                "SV Actor | 192x160", "SV Actor | 160x160", "-",
                "Load Weapons Folder", "-", "Format Current Sheet to MZ",
                "Format Whole Folder to MZ", "-",
                "Open Holder's itch.io Page"]
        }

        for creator, actions in creator_menus.items():
            self.creator_menus[creator] = (self.sub_menus[
                "Creator Compatibility"].addMenu(creator))
            for action in actions:
                if action == "-":
                    self.creator_menus[creator].addSeparator()
                else:
                    self.creator_menus[creator].addAction(action)

            for action in self.creator_menus[creator].actions():
                if (config.config_get("CREATOR") != "Holder" and action.text() in [
                        "Load Weapons Folder", "Format Current Sheet to MZ"]):
                    action.setEnabled(False)

    def create_toolbar(self):
        # Loop through our toolbar to set identical settings
        for toolbar in self.toolbars:
            toolbar.setStyleSheet(
                "QToolBar {"
                "   border-top: 1px solid black;"
                "   border-bottom: 1px solid black;"
                "   border-left: 1px solid black;"
                "   border-right: 1px solid black;"
                "   background-color: #303030;"
                "}"
                "QToolBar::separator {"
                "   width: 2px;"
                "   height: 2px;"
                "   background-color: black;"
                "}"
            )

            toolbar.setIconSize(QSize(40, 40))

            if toolbar == self.adjustment_toolbar:
                self.addToolBar(Qt.RightToolBarArea, toolbar)
            else:
                self.addToolBar(toolbar)

        action_items = [
            "New", "Open", "Add After", "Load Folder", "-", "Save Highlighted Cell(s)",
            "Save Individually Each Cell", "Save All Together"]

        for action in action_items:
            if action == "-":
                self.toolbar.addSeparator()
            else:
                # Retrieve the image which will be used as an icon for the button
                if getattr(sys, 'frozen', False):
                    parent_folder = sys._MEIPASS
                else:
                    current_path = os.path.dirname(os.path.abspath(__file__))
                    parent_folder = os.path.abspath(
                        os.path.join(current_path, "../.."))
                image_path = os.path.join(
                    parent_folder, "res/icons", f"{action}.png")

                self.toolbar_actions[action] = QAction(
                    QIcon(image_path), action, self)
                self.toolbar_actions[action].setStatusTip(action)
                self.toolbar_actions[action].hovered.connect(
                    partial(self.hovered_action, self.toolbar_actions[action]))
                self.toolbar.addAction(self.toolbar_actions[action])

        adjustment_actions_items = [
            "Offset", "Resize", "Rotate", "-", "Flip Horizontally", "Flip Vertically",
            "-", "HSV", "RGB", "-", "Play", "Stop"]

        for action in adjustment_actions_items:
            if action == "-":
                self.adjustment_toolbar.addSeparator()
            else:
                # Retrieve the image which will be used as an icon for the button
                if getattr(sys, 'frozen', False):
                    parent_folder = sys._MEIPASS
                else:
                    current_path = os.path.dirname(os.path.abspath(__file__))
                    parent_folder = os.path.abspath(
                        os.path.join(current_path, "../.."))
                image_path = os.path.join(
                    parent_folder, "res/icons", f"{action}.png")

                self.adjustment_toolbar_actions[action] = QAction(
                    QIcon(image_path), action, self)
                self.adjustment_toolbar_actions[action].setStatusTip(action)
                self.adjustment_toolbar_actions[action].hovered.connect(
                    partial(
                        self.hovered_action, self.adjustment_toolbar_actions[action]))
                self.adjustment_toolbar.addAction(
                    self.adjustment_toolbar_actions[action])

                if (action in
                        ["Flip Horizontally", "Flip Vertically", "Play", "Stop"]):
                    continue

                self.adjustment_toolbar_actions[action].setCheckable(True)

    def create_floatingframe(self):
        doc_items = ["Offset", "Resize", "Rotate", "RGB", "HSV", "Zoom"]

        for item in doc_items:
            self.frames[item] = FloatingFrame(self, item)
            if item in ["Rotate", "Resize"]:
                self.frames[item].setFixedSize(200, 180)
            else:
                self.frames[item].setFixedSize(300, 300)
            self.frames[item].setWindowTitle(item)

    def hovered_action(self, action):
        tooltip_text = action.toolTip()
        cursor_pos = self.mapFromGlobal(QCursor.pos())
        tooltip_pos = self.mapToGlobal(cursor_pos)
        window_pos = self.mapFromGlobal(tooltip_pos)
        QToolTip.showText(self.mapToGlobal(window_pos), tooltip_text)

    def create_sliders(self):
        """Creates sliders in the main window."""
        slider_items = ["Rotate", "Resize", "HSV", "RGB"]
        slider_mapping = {
            "Rotate": {
                "Rotate": SliderRotate
            },

            "Resize": {
                "Resize": SliderResize
            },

            "HSV": {
                "Hue": HueSlider,
                "Saturation": SaturationSlider,
                "Value": ValueSlider
            },

            "RGB": {
                "Red": RedSlider,
                "Green": GreenSlider,
                "Blue": BlueSlider
            }
        }

        for item in slider_items:
            layout = QGridLayout()

            for index, (key, slider) in enumerate(slider_mapping[item].items()):
                if item not in ["Rotate", "Resize"]:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setStyleSheet("background-color: #2d2d2d;")

                self.buttons[key] = QPushButton(key)
                self.values[key] = QLineEdit(
                    "Enter a value")
                self.sliders[key] = slider(self.frames[item])

                if index == 1:
                    index = 3
                elif index == 2:
                    index = 6

                layout.addWidget(self.buttons[key], index, 0, 1, 1)
                layout.addWidget(self.values[key], index, 1, 1, 1)
                layout.addWidget(self.sliders[key], index + 1, 0, 1, 2)

                if item not in ["Rotate", "Resize"]:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setStyleSheet("background-color: #2d2d2d;")
                    layout.addWidget(separator, index + 2, 0, 1, 2)

            self.frames[item].setLayout(layout)

    def create_labels(self):
        """Create labels in the main window."""
        label_items = ["Type", "Index"]
        for item in label_items:
            self.labels[item] = QLabel()
            self.labels[item].setAlignment(Qt.AlignmentFlag.AlignCenter)

            if item == "Type":
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

                self.statusbar.addPermanentWidget(self.labels[item], 0)

            elif item == "Index":
                self.labels[item].setText(
                    "Select a cell to display the index here")
                self.statusbar.addPermanentWidget(self.labels[item], 1)

    def create_buttons(self):
        """Create offset buttons in the main window."""
        widget = QWidget()
        widget.setFixedSize(190, 190)
        layout = QGridLayout(widget)

        # Retrieve the image which will be used as an icon for the button
        if getattr(sys, 'frozen', False):
            parent_folder = sys._MEIPASS
        else:
            current_path = os.path.dirname(os.path.abspath(__file__))
            parent_folder = os.path.abspath(
                os.path.join(current_path, "../.."))
        image_path = os.path.join(parent_folder, "res/icons", "arrow.png")
        offset_icon = QPixmap(image_path)

        button_items = ["Up", "Right", "Down", "Left"]
        for item in button_items:
            # Create buttons
            self.buttons[item] = QPushButton(widget)
            self.buttons[item].clicked.connect(
                partial(image_manipulation.offset, self, item))
            self.buttons[item].setFixedSize(60, 60)

            # Calculate buttons origin based on the item:
            item_mapping = {
                "Up":    {"x": 0, "y": 1, "rotation": 0},
                "Right": {"x": 1, "y": 2, "rotation": 90},
                "Down":  {"x": 2, "y": 1, "rotation": 180},
                "Left":  {"x": 1, "y": 0, "rotation": 270}
            }

            if item in item_mapping:
                adjustments = item_mapping[item]
                rotation = adjustments["rotation"]
                x = adjustments["x"]
                y = adjustments["y"]
            else:
                break

            # Rotate the image icon
            transform = QTransform().rotate(rotation)
            rotated_icon = QIcon(offset_icon.transformed(
                transform, Qt.TransformationMode.SmoothTransformation))
            self.buttons[item].setIcon(rotated_icon)
            self.buttons[item].setIconSize(QSize(32, 32))

            layout.addWidget(self.buttons[item], x, y)

        self.buttons["Change Offset"] = QPushButton("Change Offset")
        layout.addWidget(self.buttons["Change Offset"], 3, 0, 1, 3)

        self.frames["Offset"].setLayout(layout)
        self.frames["Offset"].setFixedSize(200, 230)

    def create_views(self):
        self.layout.addWidget(
            self.zoom_view, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addLayout(self.sub_layout)
        self.layout.addWidget(self.main_view)

    def create_progress_bar(self):
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumWidth(200)
        self.statusbar.addPermanentWidget(self.progress_bar)

    def eventFilter(self, obj, event):
        # Check for focus events for the floating frame
        if (isinstance(obj, FloatingFrame)):
            if event.type() == QEvent.WindowActivate:
                obj.setWindowOpacity(1.0)
            elif event.type() == QEvent.WindowDeactivate:
                obj.setWindowOpacity(0.7)

        return super().eventFilter(obj, event)


class MarkdownViewer(QMainWindow):
    def __init__(self, title, file_path):
        super().__init__()

        self.setWindowTitle(title)
        self.setFixedSize(800, 800)
        self.browser = QTextBrowser()
        self.browser.setReadOnly(True)
        self.setCentralWidget(self.browser)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.load_md_file(file_path)

    def load_md_file(self, file_path):
        with open(file_path, 'r') as file:
            md_content = file.read()

        html_content = markdown.markdown(md_content)
        self.browser.setHtml(html_content)
