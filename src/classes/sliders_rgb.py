#!/usr/bin/env python
"""slider_rgb.py"""
from PySide6.QtCore import QEventLoop, Qt, QThread, Signal
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QSlider
from modules import grid_manager
from modules import image_manipulation


class RedSlider(QSlider):
    """A custom slider to handle red value of a picture"""

    def __init__(self, parent):
        """
        Initialize the slider

        Args:
            - parent: The parent widget of this one
        """
        super(RedSlider, self).__init__(parent)

        # Set slider parameters
        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(0)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(
            lambda value: self.change_rgb(parent, value, "red"))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

    def change_rgb(self, app, value, color):
        """
        Start a thread which will be responsible of changing color

        Args:
            - app: An instance of the MainWindow class
            - value: The value to change to
            - color: The color to change value
        """
        # Disconnect the changed event
        app.main_view.scene_changed_disconnected = True

        if app.main_view.highlight_selected[0]:
            # Prevent running multiple thread
            if not hasattr(self, "rgb_processor") or not self.rgb_processor.isRunning():
                # Start the thread by calling the corresponding functions
                self.rgb_processor = RgbProcessor(app, value, color)
                self.rgb_processor.image_processed.connect(
                    self.on_image_processed)
                self.rgb_processor.start()

    def on_image_processed(self, app, value, color, modified_image):
        # Convert the QImage back to a QPixmap
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(modified_image))
        app.modified_image = updated_pixmap
        app.last_rgb[color] = value
        image_manipulation.zoom(app, updated_pixmap)

    def on_slider_end(self, app):
        if hasattr(self, "rgb_processor") and self.rgb_processor.isRunning():
            event_loop = QEventLoop()
            self.rgb_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(0)
        self.blockSignals(False)

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        # Check if an image was modified
        if not app.modified_image:
            return

        # Get the index of the selected cell
        index = app.main_view.highlight_selected[1]

        # add the modified image to the grid
        grid_manager.add_to_grid(app, app.modified_image, index)
        image_manipulation.zoom(app, app.modified_image)

        # Reset the stored modified image
        app.modified_image = None

        # Reconnect the changed event
        app.main_view.scene_changed_disconnected = False


class GreenSlider(QSlider):
    """A custom slider to handle red value of a picture"""

    def __init__(self, parent):
        """
        Initialize the slider

        Args:
            - parent: The parent widget of this one
        """
        super(GreenSlider, self).__init__(parent)

        # Set slider parameters
        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(0)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(
            lambda value: self.change_rgb(parent, value, "green"))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

    def change_rgb(self, app, value, color):
        """
        Start a thread which will be responsible of changing color

        Args:
            - app: An instance of the MainWindow class
            - value: The value to change to
            - color: The color to change value
        """
        # Disconnect the changed event
        app.main_view.scene_changed_disconnected = True

        if app.main_view.highlight_selected[0]:
            # Prevent running multiple thread
            if not hasattr(self, "rgb_processor") or not self.rgb_processor.isRunning():
                # Start the thread by calling the corresponding functions
                self.rgb_processor = RgbProcessor(app, value, color)
                self.rgb_processor.image_processed.connect(
                    self.on_image_processed)
                self.rgb_processor.start()

    def on_image_processed(self, app, value, color, modified_image):
        # Convert the QImage back to a QPixmap
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(modified_image))
        app.modified_image = updated_pixmap
        app.last_rgb[color] = value
        image_manipulation.zoom(app, updated_pixmap)

    def on_slider_end(self, app):
        if hasattr(self, "rgb_processor") and self.rgb_processor.isRunning():
            event_loop = QEventLoop()
            self.rgb_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(0)
        self.blockSignals(False)

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        # Check if an image was modified
        if not app.modified_image:
            return

        # Get the index of the selected cell
        index = app.main_view.highlight_selected[1]

        # add the modified image to the grid
        grid_manager.add_to_grid(app, app.modified_image, index)
        image_manipulation.zoom(app, app.modified_image)

        # Reset the stored modified image
        app.modified_image = None

        # Reconnect the changed event
        app.main_view.scene_changed_disconnected = False


class BlueSlider(QSlider):
    """A custom slider to handle red value of a picture"""

    def __init__(self, parent):
        """
        Initialize the slider

        Args:
            - parent: The parent widget of this one
        """
        super(BlueSlider, self).__init__(parent)

        # Set slider parameters
        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(0)
        self.setOrientation(Qt.Horizontal)

        self.valueChanged.connect(
            lambda value: self.change_rgb(parent, value, "blue"))
        self.sliderReleased.connect(lambda: self.on_slider_end(parent))

    def change_rgb(self, app, value, color):
        """
        Start a thread which will be responsible of changing color

        Args:
            - app: An instance of the MainWindow class
            - value: The value to change to
            - color: The color to change value
        """
        # Disconnect the changed event
        app.main_view.scene_changed_disconnected = True

        if app.main_view.highlight_selected[0]:
            # Prevent running multiple thread
            if not hasattr(self, "rgb_processor") or not self.rgb_processor.isRunning():
                # Start the thread by calling the corresponding functions
                self.rgb_processor = RgbProcessor(app, value, color)
                self.rgb_processor.image_processed.connect(
                    self.on_image_processed)
                self.rgb_processor.start()

    def on_image_processed(self, app, value, color, modified_image):
        # Convert the QImage back to a QPixmap
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(modified_image))
        app.modified_image = updated_pixmap
        app.last_rgb[color] = value
        image_manipulation.zoom(app, updated_pixmap)

    def on_slider_end(self, app):
        if hasattr(self, "rgb_processor") and self.rgb_processor.isRunning():
            event_loop = QEventLoop()
            self.rgb_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(0)
        self.blockSignals(False)

        # Check if there is a selected cell
        if not app.main_view.highlight_selected[0]:
            return

        # Check if an image was modified
        if not app.modified_image:
            return

        # Get the index of the selected cell
        index = app.main_view.highlight_selected[1]

        # add the modified image to the grid
        grid_manager.add_to_grid(app, app.modified_image, index)
        image_manipulation.zoom(app, app.modified_image)

        # Reset the stored modified image
        app.modified_image = None

        # Reconnect the changed event
        app.main_view.scene_changed_disconnected = False


class RgbProcessor(QThread):
    """The thread which will be responsible of changing color"""
    image_processed = Signal(object, int, str, QImage)

    def __init__(self, app, value, color):
        """
        Initialize the thread

        Args:
            - app: An instance of the MainWindow class
            - value: The value to changed current value to.
            - color: The affected color
        """
        super().__init__()
        self.app = app
        self.value = value
        self.color = color

    def run(self):
        self.app.thread_running = True
        index = self.app.main_view.highlight_selected[1]
        image = grid_manager.get_image_at(self.app, index)

        if not image:
            return

        # Convert the pixmap to a QImage
        image = image.pixmap().toImage()

        # Create a new QImage with the same size and format as the original image
        modified_image = QImage(image.size(), QImage.Format_ARGB32)

        for x in range(image.width()):
            for y in range(image.height()):
                pixel = image.pixel(x, y)
                if pixel < 1:
                    modified_image.setPixelColor(
                        x, y, Qt.GlobalColor.transparent)
                    continue

                # Extract the alpha value from the pixel
                alpha = (pixel >> 24) & 0xFF
                pixel_color = QColor(pixel)

                # Change the appropriate color based on the slider color
                color_map = {
                    "red": pixel_color.setRed,
                    "green": pixel_color.setGreen,
                    "blue": pixel_color.setBlue
                }

                color_map[self.color](self.value)

                modified_pixel = QColor(
                    pixel_color.red(), pixel_color.green(), pixel_color.blue(), alpha)
                modified_image.setPixelColor(x, y, modified_pixel)

        self.image_processed.emit(
            self.app, self.value, self.color, modified_image)

    def stop(self):
        self.terminate()
        self.wait()
