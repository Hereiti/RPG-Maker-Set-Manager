#!/usr/bin/env python
"""main_window.py"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QGraphicsPixmapItem, QSlider
from modules import grid_manager
from modules import image_manipulation


class SliderResize(QSlider):
    def __init__(self, parent):
        super(SliderResize, self).__init__(parent)
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
        # Disconnect the changed event
        app.main_view.scene_changed_disconnected = True

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        if not grid_manager.get_image_at(app, app.main_view.highlight_selected[1]):
            return

        # Get the index and size of the selected cell
        cell_index = app.main_view.highlight_selected[1]
        cell_size = app.cell_size

        # Get the pixmap of the image in the selected cell
        icon_pixmap = grid_manager.get_image_at(app, cell_index).pixmap()
        if icon_pixmap:
            # Create a new pixmap with the resized image
            resize_pixmap = QPixmap(cell_size[0], cell_size[1])
            resize_pixmap.fill(Qt.GlobalColor.transparent)

            # Calculate the new width and height based on the resizing value
            new_width = icon_pixmap.width() * value / 100
            new_height = icon_pixmap.height() * value / 100

            # Calculate the offsets to center the resized image
            _dx = (cell_size[0] - new_width) // 2
            _dy = (cell_size[1] - new_height) // 2

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
            app.modified_image = QGraphicsPixmapItem(resize_pixmap)
            image_manipulation.zoom(app, app.modified_image)

    def on_slider_end(self, app) -> None:
        # Reconnect the changed event
        app.main_view.scene_changed_disconnected = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(100)
        self.blockSignals(False)

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_image:
            return

        # Get the index of the selected cell
        index = app.main_view.highlight_selected[1]

        # Add the modified image to the dictionary and scene
        grid_manager.add_to_grid(app, app.modified_image, index)

        app.modified_image = None
