#!/usr/bin/env python
"""slider_hsv.py"""
from PySide6.QtCore import QEventLoop, Qt, QThread, Signal
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QSlider
from modules import grid_manager
from modules import image_manipulation


class HueSlider(QSlider):
    def __init__(self, parent):
        """
        Initialize the Slider

        Args:
            - parent: The parent of this widget
        """
        super(HueSlider, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(359)
        self.setValue(179)
        self.setOrientation(Qt.Horizontal)
        self.slider_end = False

        self.valueChanged.connect(
            lambda value: self.change_hsv(parent.parent(), value, "hue"))
        self.sliderReleased.connect(
            lambda: self.on_slider_end(parent.parent()))

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

    def change_hsv(self, app, value, component):
        """
        Start a thread which will be responsible of changing color

        Args:
            - app: An instance of the MainWindow class
            - value: The value to change to
            - object: The hsv object to change
        """
        # Disconnect the changed event
        app.main_view.scene_changed_disconnected = True

        app.values["Hue"].setText(str(self.value()))

        if app.main_view.highlight_selected[0]:
            if (not hasattr(self, "image_processor")
                    or not self.image_processor.isRunning()):
                self.image_processor = HsvProcessor(app, value, component)
                self.image_processor.image_processed.connect(
                    self.on_image_processed)
                self.image_processor.start()

    def on_image_processed(self, app, value, component, modified_image):
        # Convert the QImage back to a QPixmap
        app.modified_images.append(QGraphicsPixmapItem(
            QPixmap.fromImage(modified_image)))
        image_manipulation.zoom(app, app.modified_images[-1])

    def on_slider_end(self, app):
        if hasattr(self, "image_processor") and self.image_processor.isRunning():
            event_loop = QEventLoop()
            self.image_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(179)
        self.blockSignals(False)

        if not app.modified_images:
            return

        # Get the index of the selected cell
        index = app.main_view.highlight_selected[1]

        grid_manager.add_to_grid(app, app.modified_images[-1], index)
        image_manipulation.zoom(app, app.modified_images[-1])

        app.modified_images = []

        # Reconnect the changed event
        app.main_view.scene_changed_disconnected = False
        self.slider_end = True


class SaturationSlider(QSlider):
    def __init__(self, parent):
        """
        Initialize the Slider

        Args:
            - parent: The parent of this widget
        """
        super(SaturationSlider, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(127)
        self.setOrientation(Qt.Horizontal)
        self.slider_end = False

        self.valueChanged.connect(
            lambda value: self.change_hsv(parent.parent(), value, "saturation"))
        self.sliderReleased.connect(
            lambda: self.on_slider_end(parent.parent()))

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

    def change_hsv(self, app, value, component):
        """
        Start a thread which will be responsible of changing color

        Args:
            - app: An instance of the MainWindow class
            - value: The value to change to
            - object: The hsv object to change
        """
        # Disconnect the changed event
        app.main_view.scene_changed_disconnected = True

        app.values["Saturation"].setText(str(self.value()))

        if app.main_view.highlight_selected[0]:
            if (not hasattr(self, "image_processor")
                    or not self.image_processor.isRunning()):
                self.image_processor = HsvProcessor(app, value, component)
                self.image_processor.image_processed.connect(
                    self.on_image_processed)
                self.image_processor.start()

    def on_image_processed(self, app, value, component, modified_image):
        # Convert the QImage back to a QPixmap
        app.modified_images.append(QGraphicsPixmapItem(
            QPixmap.fromImage(modified_image)))
        image_manipulation.zoom(app, app.modified_images[-1])

    def on_slider_end(self, app):
        if hasattr(self, "image_processor") and self.image_processor.isRunning():
            event_loop = QEventLoop()
            self.image_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(127)
        self.blockSignals(False)

        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_images:
            return

        # Get the index of the selected cell
        index = app.main_view.highlight_selected[1]

        grid_manager.add_to_grid(app, app.modified_images[-1], index)
        image_manipulation.zoom(app, app.modified_images[-1])

        app.modified_images = []

        # Reconnect the changed event
        app.main_view.scene_changed_disconnected = False
        self.slider_end = True


class ValueSlider(QSlider):
    def __init__(self, parent):
        """
        Initialize the Slider

        Args:
            - parent: The parent of this widget
        """
        super(ValueSlider, self).__init__(parent)
        self.setMinimum(-255)
        self.setMaximum(255)
        self.setValue(0)
        self.setOrientation(Qt.Horizontal)
        self.slider_end = False

        self.valueChanged.connect(
            lambda value: self.change_hsv(parent.parent(), value, "value"))
        self.sliderReleased.connect(
            lambda: self.on_slider_end(parent.parent()))

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

    def change_hsv(self, app, value, component):
        """
        Start a thread which will be responsible of changing color

        Args:
            - app: An instance of the MainWindow class
            - value: The value to change to
            - object: The hsv object to change
        """
        # Disconnect the changed event
        app.main_view.scene_changed_disconnected = True

        app.values["Value"].setText(str(self.value()))

        if app.main_view.highlight_selected[0]:
            if (not hasattr(self, "image_processor")
                    or not self.image_processor.isRunning()):
                self.image_processor = HsvProcessor(app, value, component)
                self.image_processor.image_processed.connect(
                    self.on_image_processed)
                self.image_processor.start()

    def on_image_processed(self, app, value, component, modified_image):
        # Convert the QImage back to a QPixmap
        app.modified_image = QGraphicsPixmapItem(
            QPixmap.fromImage(modified_image))
        image_manipulation.zoom(app, app.modified_image)

    def on_slider_end(self, app):
        if hasattr(self, "image_processor") and self.image_processor.isRunning():
            event_loop = QEventLoop()
            self.image_processor.finished.connect(event_loop.quit)
            event_loop.exec_()

        app.thread_running = False

        # Reset slider value
        self.blockSignals(True)
        self.setValue(0)
        self.blockSignals(False)

        if not app.main_view.highlight_selected[0]:
            return

        if not app.modified_image:
            return

        # Get the index of the selected cell
        index = app.main_view.highlight_selected[1]

        grid_manager.add_to_grid(app, app.modified_image, index)
        image_manipulation.zoom(app, app.modified_image)

        app.modified_image = []

        # Reconnect the changed event
        app.main_view.scene_changed_disconnected = False
        self.slider_end = True


class HsvProcessor(QThread):
    image_processed = Signal(object, int, str, QImage)

    def __init__(self, app, value, component):
        super().__init__()
        self.app = app
        self.value = value
        self.component = component

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

                component_map = {
                    "hue": lambda: pixel_color.setHsv(
                        self.value,
                        pixel_color.saturation(),
                        pixel_color.value(),
                        alpha
                    ),
                    "saturation": lambda: pixel_color.setHsv(
                        pixel_color.hue(),
                        self.value,
                        pixel_color.value(),
                        alpha
                    ),
                    "value": lambda: pixel_color.setHsv(
                        pixel_color.hue(),
                        pixel_color.saturation(),
                        max(0, min(pixel_color.value() + self.value, 255)),
                        alpha
                    )
                }

                component_map[self.component]()
                modified_pixel = QColor(
                    pixel_color.red(), pixel_color.green(), pixel_color.blue(), alpha)
                modified_image.setPixelColor(x, y, modified_pixel)

        self.image_processed.emit(
            self.app, self.value, self.component, modified_image)

    def stop(self):
        self.terminate()
        self.wait()
