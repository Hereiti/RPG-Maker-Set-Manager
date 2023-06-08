#================================================================================#
# File: widgets.py
# Created Date: 05-06-2023 | 12:38:35
# Author: Hereiti
#================================================================================
# Last Modified: 07-06-2023 | 16:32:41
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
import math

from functools import partial

#================================================================================#
# Third-party imports
#================================================================================#
from PySide6.QtCore import QRect, QRectF, QPoint, Qt, QThread, Signal, QEventLoop
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QImage, QPainter, QPainterPath, QPaintEvent, QPen, QPixmap, QTransform
from PySide6.QtWidgets import (QDialog, QGraphicsColorizeEffect, QGraphicsPixmapItem, QLabel,
        QMainWindow, QSlider, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QDialogButtonBox,
        QMessageBox)

#================================================================================#
# Local imports
#================================================================================#
from modules import icons
from modules import images

#================================================================================#
# Classes
#================================================================================#
class RotateSlider(QSlider):
    """
    A custom slider widget that represents a circular range from 0 to
    360 degrees.
    
    Args:
        - parent: The parent widget for this circular slider.
    """

    def __init__(self, parent) -> None:
        super(RotateSlider, self).__init__(parent)

        # Initialize slider parameters
        self.setMinimum(0)
        self.setMaximum(360)
        self.setValue(0)
        self.setSingleStep(1)
        self.setPageStep(10)

        # Create an attribute to keep track of the slider state
        self.dragging: bool = False

    def paintEvent(self, event) -> None:
        """
        Overrides the paint event handler to customize the appearance of the widget.
        This method is called automaticallyy when the widget needs to be repainted.
        """
        # Create a QPainter object to perform painting operations
        _painter = QPainter(self)
        # Enable antialiasing for smoother graphics
        _painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate the radius and the center based on widget's size
        _radius = min(self.width(), self.height()) / 2
        _center = self.rect().center()

        # Set the pen color, thickness and style for the slider
        _painter.setPen(QPen(QColor("#F6564E"), 4))
        _painter.setBrush(Qt.BrushStyle.NoBrush)

        # Define the rectangle that encloses the circle
        _rect = QRectF(
            _center.x() - _radius + 20,
            _center.y() - _radius + 20,
            _radius * 2 - 40,
            _radius * 2 - 40
        )

        # Draw the background circle
        _painter.drawEllipse(_rect)

        # Calculate the angle for the indicator
        _angle = 360 * self.value() / (self.maximum() - self.minimum())
        # Convert the angle to radians for trigonometric calculations.
        _angle_rad = _angle * math.pi / 180.0

        # Translate the coordinates to the center of the circle
        _painter.translate(_rect.center())
        # Rotate by 90 degrees clockwise.
        _painter.rotate(90)
        # Translate back to the original position
        _painter.translate(-_rect.center())

        # Set the pen color, thickness and style for the slider
        _painter.setPen(QPen(QColor("#65b7fc"), 2))
        _painter.setBrush(QColor("#65b7fc"))

        # Calculate the radius for the indicator
        _indicator_radius = _radius * 0.72
        # Calculate the x-coordinate and y-coordinate of the indicator
        _x = int(_rect.center().x() + _indicator_radius * math.cos(_angle_rad))
        _y = int(_rect.center().y() + _indicator_radius * math.sin(_angle_rad))

        # Draw the indicator as a small ellipse
        _painter.drawEllipse(QPoint(_x, _y), 5, 5)

        # End the painting operation
        _painter.end()

    def mouseMoveEvent(self, event) -> None:
        """
        Handles the mouse move event for updating the value if dragging.
        
        Args:
            - event: The mouse move event.
        """
        if self.dragging:
            self.updateValue(event.pos())

            app = self.parent()

            # Check if there is a selected cell
            if not app.main_view.highlight_selected[0]:
                return

            # Get the index and size of the selected cell
            _index = app.main_view.highlight_selected[1]
            _cell_size = app.cell_size

            # Get the image at the selected cell
            _img = images.get_image_at(app, _index)
            if _img:
                # Set the transform origin and rotation of the img pixmap
                _img.setTransformOriginPoint(_cell_size // 2, _cell_size // 2)
                _img.setRotation(self.value())

                # Get the img as a pixmap
                _pixmap = _img.pixmap()

                # Create a placeholder pixmap
                _rotate_pixmap = QPixmap(_cell_size, _cell_size)
                _rotate_pixmap.fill(Qt.GlobalColor.transparent)

                # Create a painter to draw the rotated pixmap
                _painter = QPainter(_rotate_pixmap)
                _painter.translate(_cell_size // 2, _cell_size // 2)
                _painter.rotate(_img.rotation())
                _painter.drawPixmap(-_cell_size // 2, -_cell_size // 2, _pixmap)
                _painter.end()

                # Store the modified image
                app.modified_img = QGraphicsPixmapItem(_rotate_pixmap)
                images.zoom(app, app.modified_img)

    def mousePressEvent(self, event) -> None:
        """
        Handles the mouse press event for initiating dragging and updating the value
        
        Args:
            - event: The mouse press event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = self.is_cursor_over_indicator(event.pos())
            self.updateValue(event.pos())

    def mouseReleaseEvent(self, event) -> None:
        """
        Handles the mouse release event for ending dragging and performing final actions.

        Args:
            - event: The mouse release event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

            app = self.parent()

            # Check if there is a selected cell
            if not app.main_view.highlight_selected[0]:
                return

            # Get the index of the selected cell
            _index = app.main_view.highlight_selected[1]

            # Add the modified image to the dictionary and scene
            icons.add(app, app.modified_img, _index)
            images.zoom(app, app.modified_img)

            # Reset slider value
            self.blockSignals(True)
            self.setValue(0)
            app.labels["Rotate"].setText("0°")
            self.blockSignals(False)

            app.modified_img = None

    def updateValue(self, _pos) -> None:
        """
        Updates the value based on the given position.

        Args:
            - pos: The position of the mouse cursor
        """
        _center = self.rect().center()
        _delta_x = _pos.x() - _center.x()
        _delta_y = _pos.y() - _center.y()
        _angle = (180 / math.pi) * math.atan2(_delta_y, _delta_x) - 90
        _angle = int(_angle + 360) % 360
        _value = int((self.maximum() - self.minimum()) * _angle / 360) + self.minimum()

        self.setValue(_value)
        self.update()

        self.parent().labels["Rotate"].setText(f"{_value}°")

    def is_cursor_over_indicator(self, _pos) -> None:
        """
        Checks if the curser is over the indicator

        Args:
            - pos: The position of the mouse cursor

        Returns:
            - True if the cursor is over the indicator, False otherwise.
            
        """
        _radius = min(self.width(), self.height()) / 2
        _center = self.rect().center()
        _delta_x = _pos.x() - _center.x()
        _delta_y = _pos.y() - _center.y()
        _distance = math.sqrt(_delta_x * _delta_x + _delta_y * _delta_y)
        return _distance <= _radius * 0.9

class ResizeSlider(QSlider):
    def __init__(self, parent):
        super(ResizeSlider, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(200)
        self.setValue(100)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(lambda value: self.resize(parent, value))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

    def resize(self, app, value) -> None:
        """
        Resize the image in the selected cell of the application by the specified value.

        Args:
            app: The instance of the MainWindow class.
            value: The resizing value in percentage.

        Returns:
            None.
        """
        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        # Get the index and size of the selected cell
        cell_index = app.main_view.highlight_selected[1]
        cell_size = app.cell_size

        # Get the pixmap of the image in the selected cell
        icon_pixmap = images.get_image_at(app, cell_index).pixmap()
        if icon_pixmap:
            # Create a new pixmap with the resized image
            resize_pixmap = QPixmap(cell_size, cell_size)
            resize_pixmap.fill(Qt.GlobalColor.transparent)

            # Calculate the new width and height based on the resizing value
            new_width = icon_pixmap.width() * value / 100
            new_height = icon_pixmap.height() * value / 100

            # Calculate the offsets to center the resized image
            _dx = (cell_size - new_width) // 2
            _dy = (cell_size - new_height) // 2

            # Create a transform to apply the resizing and centering
            transform = QTransform()
            transform.translate(_dx, _dy)
            transform.scale(value / 100, value / 100)
            transform.translate(-_dx, -_dy)
            icon_pixmap = icon_pixmap.transformed(transform)

            # Create a painter to draw the resized pixmap
            painter = QPainter(resize_pixmap)
            painter.drawPixmap(int(_dx), int(_dy), icon_pixmap)
            painter.end()

            # Store the modified icon as a QGraphicsPixmapItem
            app.modified_img = QGraphicsPixmapItem(resize_pixmap)
            images.zoom(app, app.modified_img)

    def on_slider_end(self, app) -> None:
        # Reset slider value
        self.blockSignals(True)
        self.setValue(100)
        self.blockSignals(False)

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_img:
            return

        # Get the index of the selected cell
        _index = app.main_view.highlight_selected[1]

        # Add the modified image to the dictionary and scene
        icons.add(app, app.modified_img, _index)
        images.zoom(app, app.modified_img)

        app.modified_img = None

class RedSlider(QSlider):
    def __init__(self, parent, red=False, green=False, blue=False):
        super(RedSlider, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(0)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(lambda value: self.change_color(parent, value, "red"))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

    def change_color(self, app, value, color) -> None:
        if app.main_view.highlight_selected[0]:
            if not hasattr(self, 'image_processor') or not self.image_processor.isRunning():
                self.image_processor = ColorProcessor(app, value, color)
                self.image_processor.image_processed.connect(self.on_image_processed)
                self.image_processor.start()

    def on_image_processed(self, app, value, color, modified_image):
        # Convert the QImage back to a QPixmap
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(modified_image))
        app.modified_img = updated_pixmap
        app.last_color[color] = value
        images.zoom(app, updated_pixmap)

    def on_slider_end(self, app) -> None:
        if hasattr(self, 'image_processor') and self.image_processor.isRunning():
            event_loop = QEventLoop()
            self.image_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(0)
        self.blockSignals(False)

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_img:
            return

        # Get the index of the selected cell
        _index = app.main_view.highlight_selected[1]

        # Add the modified image to the dictionary and scene
        icons.add(app, app.modified_img, _index)
        images.zoom(app, app.modified_img)

        app.modified_img = None

class GreenSlider(QSlider):
    def __init__(self, parent, red=False, green=False, blue=False):
        super(GreenSlider, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(0)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(lambda value: self.change_color(parent, value, "green"))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

    def change_color(self, app, value, color) -> None:
        if app.main_view.highlight_selected[0]:
            if not hasattr(self, 'image_processor') or not self.image_processor.isRunning():
                self.image_processor = ColorProcessor(app, value, color)
                self.image_processor.image_processed.connect(self.on_image_processed)
                self.image_processor.start()

    def on_image_processed(self, app, value, color, modified_image):
        # Convert the QImage back to a QPixmap
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(modified_image))
        app.modified_img = updated_pixmap
        app.last_color[color] = value
        images.zoom(app, updated_pixmap)

    def on_slider_end(self, app) -> None:
        if hasattr(self, 'image_processor') and self.image_processor.isRunning():
            event_loop = QEventLoop()
            self.image_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(0)
        self.blockSignals(False)

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_img:
            return

        # Get the index of the selected cell
        _index = app.main_view.highlight_selected[1]

        # Add the modified image to the dictionary and scene
        icons.add(app, app.modified_img, _index)
        images.zoom(app, app.modified_img)

        app.modified_img = None

class BlueSlider(QSlider):
    def __init__(self, parent, red=False, green=False, blue=False):
        super(BlueSlider, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(0)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(lambda value: self.change_color(parent, value, "blue"))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

    def change_color(self, app, value, color) -> None:
        if app.main_view.highlight_selected[0]:
            if not hasattr(self, 'image_processor') or not self.image_processor.isRunning():
                self.image_processor = ColorProcessor(app, value, color)
                self.image_processor.image_processed.connect(self.on_image_processed)
                self.image_processor.start()

    def on_image_processed(self, app, value, color, modified_image):
        # Convert the QImage back to a QPixmap
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(modified_image))
        app.modified_img = updated_pixmap
        app.last_color[color] = value
        images.zoom(app, updated_pixmap)

    def on_slider_end(self, app) -> None:
        if hasattr(self, 'image_processor') and self.image_processor.isRunning():
            event_loop = QEventLoop()
            self.image_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(0)
        self.blockSignals(False)

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_img:
            return

        # Get the index of the selected cell
        _index = app.main_view.highlight_selected[1]

        # Add the modified image to the dictionary and scene
        icons.add(app, app.modified_img, _index)
        images.zoom(app, app.modified_img)

        app.modified_img = None

class HueSlider(QSlider):
    def __init__(self, parent):
        super(HueSlider, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(359)
        self.setValue(179)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(lambda value: self.change_hue(parent, value))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

        # Apply the custom style sheet to the slider
        self.setStyleSheet('''
            QSlider::groove:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                            stop: 0 red,
                                            stop: 0.17 yellow,
                                            stop: 0.33 green,
                                            stop: 0.50 cyan,
                                            stop: 0.67 blue,
                                            stop: 0.83 magenta,
                                            stop: 1 red);
                height: 3px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #6f6f6f;
                border: 1px solid #2f2f2f;
                width: 10px;
                height: 10px;
                margin: -4px 0;
                border-radius: 3px;
            }
        ''')

    def change_hue(self, app, value) -> None:
        if app.main_view.highlight_selected[0]:
            if not hasattr(self, 'image_processor') or not self.image_processor.isRunning():
                self.image_processor = HueProcessor(app, value)
                self.image_processor.image_processed.connect(self.on_image_processed)
                self.image_processor.start()

    def on_image_processed(self, app, value, modified_image):
        # Convert the QImage back to a QPixmap
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(modified_image))
        app.modified_img = updated_pixmap
        app.last_hue = value
        images.zoom(app, updated_pixmap)

    def on_slider_end(self, app) -> None:
        if hasattr(self, 'image_processor') and self.image_processor.isRunning():
            event_loop = QEventLoop()
            self.image_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(179)
        self.blockSignals(False)

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_img:
            return

        # Get the index of the selected cell
        _index = app.main_view.highlight_selected[1]

        # Add the modified image to the dictionary and scene
        icons.add(app, app.modified_img, _index)
        images.zoom(app, app.modified_img)

        app.modified_img = None

class SaturationSlider(QSlider):
    def __init__(self, parent):
        super(SaturationSlider, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(127)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(lambda value: self.change_saturation(parent, value))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

        # Apply the custom style sheet to the slider
        self.setStyleSheet('''
            QSlider::groove:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                    stop: 0 rgba(255, 128, 128, 255),
                                    stop: 0.17 rgba(255, 255, 128, 255),
                                    stop: 0.33 rgba(128, 255, 128, 255),
                                    stop: 0.50 rgba(128, 255, 255, 255),
                                    stop: 0.67 rgba(128, 128, 255, 255),
                                    stop: 0.83 rgba(255, 128, 255, 255),
                                    stop: 1 rgba(255, 128, 128, 255));
                height: 3px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #6f6f6f;
                border: 1px solid #2f2f2f;
                width: 10px;
                height: 10px;
                margin: -4px 0;
                border-radius: 3px;
            }
        ''')

    def change_saturation(self, app, value) -> None:
        """
        Handles the mouse move event for updating the saturation value if dragging.
        
        Args:
            - app: The instance of the application.
            - value: The saturation value.
        """
        if app.main_view.highlight_selected[0]:
            if not hasattr(self, 'image_processor') or not self.image_processor.isRunning():
                self.image_processor = SaturationProcessor(app, value)
                self.image_processor.image_processed.connect(self.on_image_processed)
                self.image_processor.start()

    def on_image_processed(self, app, value, modified_image):
        # Convert the QImage back to a QPixmap
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(modified_image))
        app.modified_img = updated_pixmap
        app.last_hue = value
        images.zoom(app, updated_pixmap)

    def on_slider_end(self, app) -> None:
        # Reset slider value
        self.blockSignals(True)
        self.setValue(127)
        self.blockSignals(False)

        if hasattr(self, 'image_processor') and self.image_processor.isRunning():
            event_loop = QEventLoop()
            self.image_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_img:
            return

        # Get the index of the selected cell
        _index = app.main_view.highlight_selected[1]

        # Add the modified image to the dictionary and scene
        icons.add(app, app.modified_img, _index)
        images.zoom(app, app.modified_img)

        app.modified_img = None

class BrightnessSlider(QSlider):
    def __init__(self, parent):
        super(BrightnessSlider, self).__init__(parent)
        self.setMinimum(-255)
        self.setMaximum(255)
        self.setValue(0)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(lambda brightness: self.change_brightness(parent, brightness))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

        # Apply the custom style sheet to the slider
        self.setStyleSheet('''
            QSlider::groove:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                            stop: 0 rgba(0, 0, 0, 255),
                                            stop: 0.5 rgba(127, 127, 127, 255),
                                            stop: 1 rgba(255, 255, 255, 255));
                height: 3px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #6f6f6f;
                border: 1px solid #2f2f2f;
                width: 10px;
                height: 10px;
                margin: -4px 0;
                border-radius: 3px;
            }
        ''')

    def change_brightness(self, app, value) -> None:
        """
        Handles the mouse move event for updating the brightness value if dragging.
        
        Args:
            - app: The instance of the application.
            - brightness: The brightness value.
        """
        if app.main_view.highlight_selected[0]:
            if not hasattr(self, 'image_processor') or not self.image_processor.isRunning():
                self.image_processor = BrightnessProcessor(app, value)
                self.image_processor.image_processed.connect(self.on_image_processed)
                self.image_processor.start()

    def on_image_processed(self, app, value, modified_image):
        # Convert the QImage back to a QPixmap
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(modified_image))
        app.modified_img = updated_pixmap
        app.last_brightness = value
        images.zoom(app, updated_pixmap)

    def on_slider_end(self, app) -> None:
        # Reset slider value
        self.blockSignals(True)
        self.setValue(0)
        self.blockSignals(False)

        if hasattr(self, 'image_processor') and self.image_processor.isRunning():
            event_loop = QEventLoop()
            self.image_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_img:
            return

        # Get the index of the selected cell
        _index = app.main_view.highlight_selected[1]

        # Add the modified image to the dictionary and scene
        icons.add(app, app.modified_img, _index)
        images.zoom(app, app.modified_img)

        app.modified_img = None

class RoundLabel(QLabel):
    """
    Custom round label class.
    
    This calss extends QLabel to create a round-shaped label with
    custom painting.
    
    Args:
        - width (int): The width of the button.
        - height (int): The height of the button.
        - parent (QWidget, optinal): The parent widget. Defaults to None.
    """

    def __init__(self, width: int, height: int, parent=None) -> None:
        super().__init__(parent)

        # Set label parameters values
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        """
        Paint event handler for custom painting.

        Args:
            - event (QPaintEvent): The paint event.
        """
        _painter = QPainter(self)
        _painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create a path for the label shape
        _path = QPainterPath()
        _path.addEllipse(1, 1, self.width() - 2, self.height() - 2)

        # Fill the button background
        _painter.fillPath(_path, QBrush(QColor("#2e2e2e")))

        # Draw the border of the button
        _painter.setPen(QPen(QColor("#545454"), 1))
        _painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)

        # Set the color and font for the button text
        _font = self.font()
        _font.setPointSize(20)
        _painter.setPen(QColor(Qt.GlobalColor.white))
        _painter.setFont(_font)

        # Calculate the text rectangle and clip the text if necessary
        _rect = QRect(0, 0, self.width(), self.height()).adjusted(5, 0, -5, 0)
        _metrics = QFontMetrics(_font)
        _text = _metrics.elidedText(self.text(), Qt.TextElideMode.ElideRight, _rect.width())

        # Draw the text at the center of the label
        _painter.drawText(_rect, Qt.AlignmentFlag.AlignCenter, _text)

class TwoInputDialog(QDialog):
    def __init__(self, parent=None, title="", text_1="", value_1="", text_2="", value_2=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()

        self.text_1 = text_1
        self.value_1 = value_1
        self.text_2 = text_2
        self.value_2 = value_2

        # First text box
        self.label1 = QLabel(self.text_1)
        self.textbox1 = QLineEdit(self.value_1)
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.textbox1)

        # Second text box
        self.label2 = QLabel(self.text_2)
        self.textbox2 = QLineEdit(self.value_2)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.textbox2)

        # OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

class Form(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report Issue")

        layout = QVBoxLayout(self)

        # Add a label and line edit for single-line input
        label = QLabel("Title:")
        layout.addWidget(label)
        self.title = QLineEdit()
        layout.addWidget(self.title)

        # Add a label and text edit for multi-line input
        label = QLabel("Include a description of the issue, steps to reproduce\nand your name or a pseudonyme to be credited.")
        layout.addWidget(label)
        self.desc = QTextEdit()
        layout.addWidget(self.desc)

        label = QLabel("Any abuse of this feature will lead to this being disabled.")
        layout.addWidget(label)

        # Add OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_button_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept_button_clicked(self):
        # Validate the fields before accepting the dialog
        if self.title.text().strip() == "":
            QMessageBox.warning(self, "Error", "Title field cannot be empty.")
            return
        if self.desc.toPlainText().strip() == "":
            QMessageBox.warning(self, "Error", "Description field cannot be empty.")
            return

        # Accept the dialog
        self.accept()

class HueProcessor(QThread):
    image_processed = Signal(object, int, QImage)

    def __init__(self, app, value):
        super().__init__()
        self.app = app
        self.value = value

    def run(self):
        self.app.thread_running = True
        _index = self.app.main_view.highlight_selected[1]
        _img = images.get_image_at(self.app, _index)

        if _img is None:
            return

        # Convert the pixmap to a QImage
        image = _img.pixmap().toImage()

        # Create a new QImage with the same size and format as the original image
        modified_image = QImage(image.size(), QImage.Format_ARGB32)

        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixel(x, y)
                if pixel < 1:
                    modified_image.setPixelColor(x, y, Qt.GlobalColor.transparent)
                    continue
                alpha = (pixel >> 24) & 0xFF  # Extract the alpha value from the pixel value
                pixel_color = QColor(pixel)
                pixel_color.setHsv(self.value, pixel_color.saturation(), pixel_color.value(), alpha)
                modified_pixel = QColor(pixel_color.red(), pixel_color.green(), pixel_color.blue(), alpha)
                modified_image.setPixelColor(x, y, modified_pixel)

        self.image_processed.emit(self.app, self.value, modified_image)

    def stop(self):
        self.terminate()
        self.wait()

class SaturationProcessor(QThread):
    image_processed = Signal(object, int, QImage)

    def __init__(self, app, value):
        super().__init__()
        self.app = app
        self.value = value

    def run(self):
        self.app.thread_running = True
        _index = self.app.main_view.highlight_selected[1]
        _img = images.get_image_at(self.app, _index)

        if _img is None:
            return

        # Convert the pixmap to a QImage
        image = _img.pixmap().toImage()

        # Create a new QImage with the same size and format as the original image
        modified_image = QImage(image.size(), QImage.Format_ARGB32)

        # Apply colorizing effect to the QImage
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixel(x, y)
                if pixel < 1:
                    modified_image.setPixelColor(x, y, Qt.GlobalColor.transparent)
                    continue
                alpha = (pixel >> 24) & 0xFF  # Extract the alpha value from the pixel value
                pixel_color = QColor(pixel)
                pixel_color.setHsv(pixel_color.hue(), self.value, pixel_color.value(), alpha)
                modified_pixel = QColor(pixel_color.red(), pixel_color.green(), pixel_color.blue(), alpha)
                modified_image.setPixelColor(x, y, modified_pixel)

        self.image_processed.emit(self.app, self.value, modified_image)

    def stop(self):
        self.terminate()
        self.wait()

class BrightnessProcessor(QThread):
    image_processed = Signal(object, int, QImage)

    def __init__(self, app, value):
        super().__init__()
        self.app = app
        self.value = value

    def run(self):
        self.app.thread_running = True
        _index = self.app.main_view.highlight_selected[1]
        _img = images.get_image_at(self.app, _index)

        if _img is None:
            return

        # Convert the pixmap to a QImage
        image = _img.pixmap().toImage()

        # Create a new QImage with the same size and format as the original image
        modified_image = QImage(image.size(), QImage.Format_ARGB32)

        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixel(x, y)
                if pixel < 1:
                    modified_image.setPixelColor(x, y, Qt.GlobalColor.transparent)
                    continue
                alpha = (pixel >> 24) & 0xFF  # Extract the alpha value from the pixel value
                pixel_color = QColor(pixel)
                pixel_color.setHsv(pixel_color.hue(), pixel_color.saturation(), max(0, min(pixel_color.value() + self.value, 255)), alpha)
                modified_pixel = QColor(pixel_color.red(), pixel_color.green(), pixel_color.blue(), alpha)
                modified_image.setPixelColor(x, y, modified_pixel)

        self.image_processed.emit(self.app, self.value, modified_image)

    def stop(self):
        self.terminate()
        self.wait()

class ColorProcessor(QThread):
    image_processed = Signal(object, int, str, QImage)

    def __init__(self, app, value, color):
        super().__init__()
        self.app = app
        self.value = value
        self.color = color

    def run(self):
        self.app.thread_running = True
        _index = self.app.main_view.highlight_selected[1]
        _img = images.get_image_at(self.app, _index)

        if _img is None:
            return

        # Convert the pixmap to a QImage
        image = _img.pixmap().toImage()

        # Create a new QImage with the same size and format as the original image
        modified_image = QImage(image.size(), QImage.Format_ARGB32)

        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixel(x, y)
                if pixel < 1:
                    modified_image.setPixelColor(x, y, Qt.GlobalColor.transparent)
                    continue
                alpha = (pixel >> 24) & 0xFF  # Extract the alpha value from the pixel value
                pixel_color = QColor(pixel)

                if self.color == "red":
                    pixel_color.setRed(self.value)  # Change the red value
                elif self.color == "blue":
                    pixel_color.setBlue(self.value) # Change the blue value
                elif self.color == "green":
                    pixel_color.setGreen(self.value) # Change the green value

                modified_pixel = QColor(pixel_color.red(), pixel_color.green(), pixel_color.blue(), alpha)
                modified_image.setPixelColor(x, y, modified_pixel)

        self.image_processed.emit(self.app, self.value, self.color, modified_image)

    def stop(self):
        self.terminate()
        self.wait()