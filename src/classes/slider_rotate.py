#!/usr/bin/env python
"""slider_rotate.py"""
import math
from PySide6.QtCore import QRectF, QRect, Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QSlider
from classes.labels import RoundLabel
from modules import grid_manager


class SliderRotate(QSlider):
    """
    A custom slider widget that represents a circular range from 0 to 360 degrees.

    Args:
        - parent: The parent widget for this circular slider.

    Methods:
        paintEvent: draw the widget
        mouseMoveEvent: handles mouse movement event
        mousePressEvent: handles mouse press event
        mouseReleaseEvent: handles mouse release event
        is_cursor_over_indicator: check if the cursor is on top of the indicator
        updateValue: update the value of the slider based on indicator pos
    """

    def __init__(self, parent):
        "Initialize the slider"
        super(SliderRotate, self).__init__(parent)

        # Initialize slider parameters
        self.setMinimum(0)
        self.setMaximum(360)
        self.setValue(0)
        self.setFixedSize(140, 140)
        self.images = []

        self.label = RoundLabel(80, 80, self)
        self.label.setGeometry(QRect(29, 28, 80, 80))
        self.label.setText("0°")

        # Create an attribute to keep track of the slider state
        self.dragging: bool = False

    def paintEvent(self, event):
        """
        Overrides the paint event handler to customize the apparance of the widget.
        This method is called automatically when the widget needs to be repainted.
        """
        # Create a QPainter object to perform painting operations
        painter = QPainter(self)

        # Enable antialiasing for smoother graphics
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate the radius and the center based on widget's size
        radius = min(self.width(), self.height()) / 2
        center = self.rect().center()

        # Set the pen color, thickness and style for the slider
        painter.setPen(QPen(QColor("#F6564E"), 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Define the rectangle that enclises the circle
        rect = QRectF(
            center.x() - radius + 20,
            center.y() - radius + 20,
            radius * 2 - 40,
            radius * 2 - 40
        )

        # Draw the background circle
        painter.drawEllipse(rect)

        # Calculate the angle for the indicator
        angle = 360 * self.value() / (self.maximum() - self.minimum())
        # Convert the angle to radians for trigonometric calculations
        angle_rad = angle * math.pi / 180

        # Translate the coordinates to the center of the circle and apply rotation
        painter.translate(rect.center())
        painter.rotate(90)
        painter.translate(-rect.center())

        # Set the pen color, thickness and style for the indicator
        painter.setPen(QPen(QColor("#65b7fc"), 2))
        painter.setBrush(QColor("#65b7fc"))

        # Calculate the radius for the indicator
        indicator_radius = radius * 0.72
        # Calculate the x-coordinate and y-coordinate of the indicator
        x = int(rect.center().x() + indicator_radius * math.cos(angle_rad))
        y = int(rect.center().y() + indicator_radius * math.sin(angle_rad))

        # Draw the indicator as a small circle
        painter.drawEllipse(QPoint(x, y), 5, 5)
        painter.end()

    def mouseMoveEvent(self, event):
        """
        Handles the mouse move event for updating the value if dragging.

        Args:
            - event: The mouse move event.
        """
        if self.dragging:
            self.updateValue(event.pos())

            app = self.parent().parent()
            app.values["Rotate"].setText(str(self.value()))

            # Check if there is a selected cell
            if (not app.main_view.highlight_selected[0]
                    and not len(app.main_view.mass_highlight) > 0):
                return

            cell_width, cell_height = app.cell_size

            if app.main_view.highlight_selected[0]:
                # Get the index and size of the selected cell
                index = app.main_view.highlight_selected[1]

                # Get the image at the selected cell
                self.images.append((grid_manager.get_image_at(app, index)))
            else:
                for highlight, index in app.main_view.mass_highlight:
                    self.images.append((grid_manager.get_image_at(app, index)))

            for image in self.images:
                if image is None:
                    continue
                app.scene_changed_disconnected = True
                # Set the transform origin and rotation of the image
                image.setTransformOriginPoint(
                    cell_width // 2, cell_height // 2)
                image.setRotation(self.value())

                # Get the transformed image as a pixmap
                image_pixmap = image.pixmap()

                # Create a placeholder pixmap
                placeholder_pixmap = QPixmap(cell_width, cell_height)
                placeholder_pixmap.fill(Qt.GlobalColor.transparent)

                # Create a painter to draw the rotated pixmap
                painter = QPainter(placeholder_pixmap)
                painter.translate(cell_width // 2, cell_height // 2)
                painter.rotate(image.rotation())
                painter.drawPixmap(-cell_width // 2,
                                   -cell_height // 2, image_pixmap)
                painter.end()

    def mousePressEvent(self, event):
        """
        Handles the mouse press event for initiating dragging and updating the value

        Args:
            - event: The mouse press event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = self.is_cursor_over_indicator(event.pos())
            if self.dragging:
                self.updateValue(event.pos())

    def mouseReleaseEvent(self, event):
        """
        Handles the mouse release event for ending dragging

        Args:
            - event: The mouse release event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

            app = self.parent().parent()

            # Check if there is a selected cell
            if (not app.main_view.highlight_selected
                    and not len(app.main_view.mass_highlight) > 0):
                return

            if not app.images:
                return

            cell_width, cell_height = app.cell_size

            for image in self.images:
                if image is None:
                    continue
                app.scene_changed_disconnected = True
                # Set the transform origin and rotation of the image
                image.setTransformOriginPoint(
                    cell_width // 2, cell_height // 2)
                image.setRotation(self.value())

                # Get the transformed image as a pixmap
                image_pixmap = image.pixmap()

                # Create a placeholder pixmap
                placeholder_pixmap = QPixmap(cell_width, cell_height)
                placeholder_pixmap.fill(Qt.GlobalColor.transparent)

                # Create a painter to draw the rotated pixmap
                painter = QPainter(placeholder_pixmap)
                painter.translate(cell_width // 2, cell_height // 2)
                painter.rotate(image.rotation())
                painter.drawPixmap(-cell_width // 2,
                                   -cell_height // 2, image_pixmap)
                painter.end()

                # Store the modified image
                app.modified_images.append(
                    QGraphicsPixmapItem(placeholder_pixmap))

            app.scene_changed_disconnected = False

            # Check if there is a selected cell
            if (not app.main_view.highlight_selected[0]
                    and not len(app.main_view.mass_highlight) > 0):
                return

            if app.main_view.highlight_selected[0]:
                grid_manager.add_to_grid(
                    app, app.modified_images[0], app.main_view.highlight_selected[1])
            else:
                number = 0
                for highlight, index in app.main_view.mass_highlight:
                    if (grid_manager.get_image_at(app, index)) is None:
                        continue

                    grid_manager.add_to_grid(
                        app, app.modified_images[number], index)

                    number += 1

            app.modified_images = []
            self.images = []

            # Reset slider value
            self.blockSignals(True)
            self.setValue(0)
            self.blockSignals(False)

            self.label.setText("0°")

    def updateValue(self, pos):
        """
        Updates the value based on the given position

        Args:
            - pos: The position of the mouse cursor
        """
        center = self.rect().center()
        delta_x = pos.x() - center.x()
        delta_y = pos.y() - center.y()
        angle = int((180 / math.pi) *
                    math.atan2(delta_y, delta_x) - 90 + 360) % 360
        value = int((self.maximum() - self.minimum())
                    * angle / 360) + self.minimum()

        self.setValue(value)
        self.update()

        self.label.setText(f"{value}°")

    def is_cursor_over_indicator(self, pos):
        """
        Checks if the cursor is over the indicator

        Args:
            - pos: The position of the mouse cursor

        Returns:
            - True if the cursor is over the indicator, False otherwise
        """
        radius = min(self.width(), self.height()) / 2
        center = self.rect().center()
        delta_x = pos.x() - center.x()
        delta_y = pos.y() - center.y()
        distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)
        return distance <= radius * 0.8 and distance >= radius * 0.60
