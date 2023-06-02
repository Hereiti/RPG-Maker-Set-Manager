#================================================================================#
# File: Widget.py
# Created Date: 25-05-2023 | 09:31:15
# Author: Hereiti
#================================================================================
# Last Modified: 02-06-2023 | 11:24:27
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Imports
#================================================================================#
import math

#================================================================================#
# Third-Party Imports
#================================================================================#
from PySide6.QtCore    import QRectF, Qt, QPoint, QRect
from PySide6.QtGui     import QPainter, QPen, QColor, QPainterPath, QPaintEvent, QBrush, QFontMetrics
from PySide6.QtWidgets import QSlider, QPushButton

#================================================================================#
# Local Application Imports
#================================================================================#
from modules import edits

#================================================================================#
# Classes
#================================================================================#
class CircularSlider(QSlider):
    """
    A custom slider widget that represents a circular range from 0 to 360 degrees.
    Args:
        parent: The parent widget for this circular slider.
    """
    def __init__(self, parent) -> None:
        """
        A custom slider widget that represents a circular range from 0 to 360 degrees.
        Args:
            parent: The parent widget for this circular slider.
        """
        super(CircularSlider, self).__init__(parent)

        # Set the minimum value of the slider to 0.
        self.setMinimum(0)
        # Set the maximum value of the slider to 360.
        self.setMaximum(360)
        # Set the initial value of the slider to 0.
        self.setValue(0)
        # Set the amount by which the slider's value changes with each step.
        self.setSingleStep(1)
        # Set the amount by which the slider's value changes with each page step.
        self.setPageStep(10)
        # Set the position of the tick marks below the slider.
        self.setTickPosition(QSlider.TickPosition.TicksBelow)
        # Variable to keep track of the current dragging state of the slider.
        self.dragging = None

    def paintEvent(self, event) -> None:
        """
        Overrides the paint event handler to customize the appearance of the widget.
        This method is called automatically when the widget needs to be repainted.
        Note: This code assumes that the class inherits from QWidget or a subclass of it.
        """
        # Create a QPainter object to perform painting operations on the widget.
        painter = QPainter(self)
        # Enable antialiasing for smoother graphics.
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate the radius based on the widget's size.
        radius = min(self.width(), self.height()) / 2
        # Calculate the center point of the widget's rectangle.
        center = self.rect().center()

        # Define the background color for the circular slider.
        background_color = QColor(246, 86, 78)
        # Set the pen color and thickness for drawing the circle.
        painter.setPen(QPen(background_color, 4))
        # Set the brush style to no brush for filling the circle.
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Define the rectangle that encloses the circle.
        rect = QRectF(
            center.x() - radius + 20,
            center.y() - radius + 20,
            radius * 2 - 40,
            radius * 2 - 40,
        )
        # Draw the background circle.
        painter.drawEllipse(rect)

        # Calculate the angle for the indicator.
        angle = 360 * self.value() / (self.maximum() - self.minimum())
        # Convert the angle to radians for trigonometric calculations.
        angle_rad = angle * math.pi / 180.0

        # Translate the coordinate system to the center of the circle.
        painter.translate(rect.center())
        # Rotate the coordinate system by 90 degrees clockwise.
        painter.rotate(+90)
        # Translate the coordinate system back to its original position.
        painter.translate(-rect.center())

        # Define the color for the indicator.
        indicator_color = QColor("#65b7fc")
        # Set the pen color and thickness for drawing the indicator.
        painter.setPen(QPen(indicator_color, 2))
        # Set the brush color for filling the indicator.
        painter.setBrush(indicator_color)

        # Calculate the radius for the indicator.
        indicator_radius = radius * 0.72
        # Calculate the x-coordinate of the indicator.
        _x = int(rect.center().x() + indicator_radius * math.cos(angle_rad))
        # Calculate the y-coordinate of the indicator.
        _y = int(rect.center().y() + indicator_radius * math.sin(angle_rad))

        # Draw the indicator as a small ellipse.
        painter.drawEllipse(QPoint(_x, _y), 5, 5)

        # End the painting operations.
        painter.end()

    def mouseMoveEvent(self, event) -> None:
        """
        Handles the mouse move event for updating the value if dragging.
        Args:
            event: The mouse move event.
        """
        if self.dragging:
            self.updateValue(event.pos())

    def mousePressEvent(self, event) -> None:
        """
        Handles the mouse press event for initiating dragging and updating the value.
        Args:
            event: The mouse press event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = self.is_cursor_over_indicator(event.pos())
            self.updateValue(event.pos())

    def mouseReleaseEvent(self, event) -> None:
        """
        Handles the mouse release event for ending dragging and performing final actions.
        Args:
            event: The mouse release event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            edits.on_slider_end(self.parent())

    def updateValue(self, pos) -> None:
        """
        Updates the value based on the given position.
        Args:
            pos: The position of the mouse cursor.
        """
        center = self.rect().center()
        delta_x = pos.x() - center.x()
        delta_y = pos.y() - center.y()
        angle = (180 / math.pi) * math.atan2(delta_y, delta_x) - 90
        angle = (
            int(angle + 360) % 360
        )  # Adjust the angle to be in the range of 0-360 degrees
        value = int((self.maximum() - self.minimum()) * angle / 360) + self.minimum()
        self.setValue(value)
        self.update()
        
        edits.rotate_image(self.parent(), value)

    def is_cursor_over_indicator(self, pos) -> None:
        """
        Checks if the cursor is over the indicator.
        Args:
            pos: The position of the mouse cursor.
        Returns:
            True if the cursor is over the indicator, False otherwise.
        """
        radius = min(self.width(), self.height()) / 2
        center = self.rect().center()
        delta_x = pos.x() - center.x()
        delta_y = pos.y() - center.y()
        distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)
        return distance <= radius * 0.9

class RoundButton(QPushButton):
    """Custom round button class.

    This class extends QPushButton to create a round-shaped button with custom painting.

    Args:
        width (int): The width of the button.
        height (int): The height of the button.
        parent (QWidget, optional): The parent widget. Defaults to None.
    """

    def __init__(self, width: int, height: int, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setEnabled(False)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint event handler for custom button painting.

        Args:
            event (QPaintEvent): The paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create a path for the button shape
        path = QPainterPath()
        path.addEllipse(1, 1, self.width() - 2, self.height() - 2)

        # Fill the button with a background color
        button_color = QColor("#2e2e2e")
        painter.fillPath(path, QBrush(button_color))

        # Draw the border of the button
        border_color = QColor("#545454")
        border_width = 1
        painter.setPen(QPen(border_color, border_width))
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)

        # Set the color and font for the button text
        text_color = QColor(Qt.GlobalColor.white)
        painter.setPen(text_color)
        font = self.font()
        font.setPointSize(20)
        painter.setFont(font)

        # Calculate the text rectangle and clip the text if necessary
        text_rect = QRect(0, 0, self.width(), self.height()).adjusted(5, 0, -5, 0)
        metrics = QFontMetrics(font)
        clipped_text = metrics.elidedText(self.text(), Qt.TextElideMode.ElideRight, text_rect.width())

        # Draw the clipped text at the center of the button
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, clipped_text)
