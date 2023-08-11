#!/usr/bin/env python
"""graphics_view.py"""
from PySide6.QtCore import QRect, Qt, QRectF, QPointF
from PySide6.QtGui import QImage, QPainter, QPen, QBrush, QTransform
from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsPixmapItem)
from classes.item_grid import Grid
from classes.item_highlight import Highlight
from modules import files
from modules import grid_manager
from modules import image_manipulation
from modules import maths
from modules import utils


class GraphicsView(QGraphicsView):
    """Custom QGraphicsView for handling graphics interactions."""

    def __init__(self, parent=None):
        """Initialize the GraphicsView"""
        super().__init__(parent)

        # Initialize attributes
        self.unique_index = []
        self.mass_highlight = []
        self.highlight_selected = (None, None)
        self.app = self.parent().parent()
        self.cell_width, self.cell_height = self.app.cell_size

        # Store the initial mouse position
        self.last_mouse_pos = None
        self.zoom_factor = 1.0

        # Initialize more attributes for the drag event
        self.drag_item = None
        self.drag_highlight = None
        self.drag_indexes = [None, None]

        self.scene_changed_disconnected = False

        # More attributes but for the drag selection rect
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.dragging = False
        self.start_point = None
        self.end_point = None
        self.rect_item = None
        self.start_index = None
        self.end_index = None

        # Set the viewport update mode to ensure only visible portions are drawn
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)

        # Create a scene
        self.scene = QGraphicsScene()
        width = maths.grid_col() * self.cell_width
        height = maths.grid_row() * self.cell_height
        self.scene.setSceneRect(0, 0, width, height)
        self.setSceneRect(
            -3,
            -self.cell_height,
            width + 5,
            height + 2 + self.cell_height * 2)
        self.setScene(self.scene)
        self.scene.changed.connect(lambda: self.scene_changed())

        # Draw the grid
        self.grid = Grid(
            maths.grid_col(),
            maths.grid_row(),
            self.cell_width,
            self.cell_height
        )
        self.scene.addItem(self.grid)

    def mousePressEvent(self, event):
        """Handles mouse press event."""
        # Prevent running if a thread is running
        if self.app.thread_running:
            return

        if event.button() == Qt.MouseButton.MiddleButton:
            # Store the initial mouse position
            self.last_mouse_pos = event.pos()
            event.accept()

        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True

            # Map the mouse cursor position to the scene coordinates
            scene_pos = self.mapToScene(event.pos())

            self.start_point = QPointF(scene_pos)
            self.end_point = QPointF(scene_pos)
            self.rect_item = self.scene.addRect(
                QRectF(self.start_point, self.end_point).normalized(),
                QPen("#4800FF"),
                QBrush("#0098FF"))
            self.rect_item.setOpacity(0.3)

        if event.button() == Qt.MouseButton.RightButton:
            self.scene_changed_disconnected = True

            # Return if there is no image loaded
            if not self.app.images:
                return

            # Map the mouse cursor position to the scene coordinates
            scene_pos = self.mapToScene(event.pos())
            x, y = scene_pos.x(), scene_pos.y()

            # Get the cell index and origin
            index = maths.cell_index(x, y)
            origin = maths.cell_origin(index)

            # Create a highlight and place it at the clicked cell
            self.drag_highlight = Highlight(
                "green", self.cell_width, self.cell_height)
            self.drag_highlight.setPos(*origin)
            self.scene.addItem(self.drag_highlight)

            # Create QRect representing the clicked cell
            cell_rect = QRect(*origin, self.cell_width, self.cell_height)

            # Check for collision between the highlight and other items
            _item = None
            for item in self.scene.items(cell_rect):
                if isinstance(item, QGraphicsPixmapItem):
                    if item.collidesWithItem(self.drag_highlight):
                        if item in self.app.images.values():
                            _item = item
                            break

            if _item is not None:
                # Store the item and its initial index
                _item.setZValue(1)
                self.drag_item = _item
                self.drag_indexes[0] = index

    def mouseMoveEvent(self, event):
        """Handles mouse move event"""
        # Prevent running if a thread is running.
        if self.app.thread_running:
            return

        if self.last_mouse_pos is not None:
            # Calculate the difference in mouse position
            diff = event.pos() - self.last_mouse_pos

            # Adjust the position of the viewport by scrolling
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - diff.x())
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - diff.y())

            # Update the last mouse position
            self.last_mouse_pos = event.pos()

            # Update the scene's visible rectangle to match the new viewport position
            scene_rect = self.sceneRect()
            scene_rect.translate(- diff.x(), - diff.y())
            self.setSceneRect(scene_rect)

            event.accept()

        if self.dragging:
            # Map the mouse cursor position to the scene coordinates
            scene_pos = self.mapToScene(event.pos())

            self.end_point = QPointF(scene_pos)
            self.rect_item.setRect(
                QRectF(self.start_point, self.end_point).normalized())

        if self.drag_item and self.drag_indexes[0]:
            if self.app.animation and self.app.animation[0] is not None:
                image_manipulation.stop_animations[self.app]

            if not self.drag_highlight:
                return

            # Map the mouse cursor position to the scene coordinates
            scene_pos = self.mapToScene(event.pos())
            x, y = scene_pos.x(), scene_pos.y()

            # Get the current cell index and clamp it within the grid bounds
            index = maths.cell_index(int(x), int(y))
            index = (
                min(max(index[0], 0), maths.grid_col() - 1),
                min(max(index[1], 0), maths.grid_row() - 1)
            )

            # Calculate the origin of the cell
            origin = maths.cell_origin(index)

            # Move the item and highlight to the current cell
            self.drag_item.setPos(*origin)
            self.drag_highlight.setPos(*origin)

            # Create a QRect representing the current cell
            cell_rect = QRect(*origin, self.cell_width, self.cell_height)

            # Check for collision between other items and the highlight
            _item = None
            for item in self.scene.items(cell_rect):
                if isinstance(item, QGraphicsPixmapItem):
                    if item.collidesWithItem(self.drag_highlight):
                        if item in self.app.images.values():
                            if item != self.drag_item:
                                _item = item
                                _item.setZValue(0)
                                break

            # Update the drag_indexes[1] value to current cell index
            self.drag_indexes[1] = index
            image_manipulation.zoom(
                self.app, grid_manager.get_image_at(
                    self.app, self.drag_indexes[1]
                ))

    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""

        if event.button() == Qt.MouseButton.MiddleButton:
            # Reset the last mouse position
            self.last_mouse_pos = None
            event.accept()

        # Prevent running if a thread is running.
        if self.app.thread_running:
            return

        # Reconnect the changed event
        self.scene_changed_disconnected = False

        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.scene.removeItem(self.rect_item)
            self.rect_item = None

            start_col, start_row = maths.cell_index(
                self.start_point.x(), self.start_point.y())

            end_col, end_row = maths.cell_index(
                self.end_point.x(), self.end_point.y())

            if self.start_point.x() < 0 and self.end_point.x() < 0:
                return

            if start_col > maths.grid_col() and end_col > maths.grid_col():
                return

            if start_row > maths.grid_row() and end_row > maths.grid_row():
                return

            if self.start_point != self.end_point:
                self.start_index = maths.cell_index(
                    self.start_point.x(), self.start_point.y())
                self.end_index = maths.cell_index(
                    self.end_point.x(), self.end_point.y())

                cells = []
                if self.start_index[0] <= self.end_index[0]:
                    x_range = range(
                        self.start_index[0], self.end_index[0] + 1)
                else:
                    x_range = range(
                        self.start_index[0], self.end_index[0] - 1, -1)

                if self.start_index[1] <= self.end_index[1]:
                    y_range = range(
                        self.start_index[1], self.end_index[1] + 1)
                else:
                    y_range = range(
                        self.start_index[1], self.end_index[1] - 1, -1)

                for x in x_range:
                    for y in y_range:
                        cells.append((x, y))

                if not event.modifiers() or not Qt.KeyboardModifier.ControlModifier:
                    if len(self.mass_highlight) > 0:
                        for highlight, index in self.mass_highlight:
                            self.scene.removeItem(highlight)

                        self.mass_highlight.clear()
                        self.unique_index.clear()

                    if self.highlight_selected[0]:
                        self.scene.removeItem(self.highlight_selected[0])

                    self.highlight_selected = [None, None]

                    if len(cells) == 1:
                        grid_manager.click_cell(event, self.app)
                        return

                max_value = len(cells)
                self.app.progress_bar.setVisible(True)
                current_value = 0

                for index in cells:
                    current_value += 1
                    progress = current_value / max_value * 100
                    self.app.progress_bar.setValue(progress)

                    if progress >= 100:
                        self.app.progress_bar.setVisible(False)
                        self.app.progress_bar.setValue(0)

                    grid_manager.highlight_index(
                        self.app, index, "mass")
            else:
                if event.modifiers() and Qt.KeyboardModifier.ControlModifier:
                    grid_manager.click_cell(
                        event, self.app, "mass")
                else:
                    grid_manager.click_cell(event, self.app)

            self.start_point = None
            self.end_point = None

        if event.button() == Qt.MouseButton.RightButton:
            if self.drag_highlight is not None:
                # Remove the highlight from the scene
                self.scene.removeItem(self.drag_highlight)
                self.drag_highlight = None

            if all(index is not None for index in self.drag_indexes):
                if self.drag_indexes[0] == self.drag_indexes[1]:
                    # Reset drag_item and drag_indexes
                    self.drag_indexes = [None, None]
                    self.drag_item = None
                    return

                images = self.app.images
                index_a, index_b = self.drag_indexes

                # Check if the shift key is held down for item switching
                if event.modifiers() and Qt.KeyboardModifier.ShiftModifier:
                    item_a = images.get(index_a)
                    item_b = images.get(index_b)

                    origin_a = maths.cell_origin(index_a)
                    origin_b = maths.cell_origin(index_b)

                    if item_a:
                        item_a.setPos(*origin_b)
                        images[index_b] = item_a

                    if item_b:
                        item_b.setPos(*origin_a)
                        images[index_a] = item_b

                    utils.history(
                        self.app, "MOVE", self.drag_indexes, None, "SWITCH")

                else:
                    # Simply overwrite the new cell
                    temp_path = None
                    if index_b in images:
                        temp_path = grid_manager.remove_from_grid(
                            self.app, index_b)

                    self.drag_item.setPos(*maths.cell_origin(index_b))
                    images[index_b] = self.drag_item
                    del images[index_a]

                    utils.history(
                        self.app, "MOVE", self.drag_indexes, temp_path, "OVERWRITE")

                # Reset attributes
                self.drag_item = None
                self.drag_indexes = [None, None]

    def mouseDoubleClickEvent(self, event):
        """Handles mouse double-click event."""
        # Prevent running if a thread is running
        if self.app.thread_running:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            # Prompt for an image file
            image = files.prompt_file(self.app)

            if image:
                grid_manager.add_to_grid(
                    self.app, image, self.highlight_selected[1])

    def dropEvent(self, event):
        """Handles the drop event."""
        # Prevent running if a thread is running
        if self.app.thread_running:
            return

        # Map the event position to scene coordinates
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()

        # Calculate the cell index and origin
        cell_index = maths.cell_index(x, y)
        cell_origin = maths.cell_origin(cell_index)

        # Check if the click is out of bounds
        limit = maths.cell_origin((maths.grid_col() - 1, maths.grid_row() - 1))
        if any(coord < 0 or coord > limit for coord, limit, in zip(cell_origin, limit)):
            return

        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile() and url.toLocalFile().endswith(".png"):
                    # Call the function with the dropped image file path
                    image = QImage(url.toLocalFile())

                    # Map the mouse cursor position to the scene coordinates
                    scene_pos = self.mapToScene(event.pos())
                    x, y = scene_pos.x(), scene_pos.y()

                    # Get the current cell index
                    index = maths.cell_index(int(x), int(y))

                    if (image.width() <= self.cell_width
                            and image.height() <= self.cell_height):
                        # Add a single image
                        grid_manager.add_to_grid(self.app, image, index)

                    else:
                        # Load the whole image
                        grid_manager.load(self.app, image, True, False, index)

    def dragMoveEvent(self, event):
        """Handles drag move event."""
        # Prevent running if a thread is running
        if self.app.thread_running:
            return

        event.acceptProposedAction()

    def keyPressEvent(self, event):
        """Handles key press event."""
        # Prevent running if a thread is running
        if self.app.thread_running:
            return

        # Remove the image if the del key is pressed
        if event.key() == Qt.Key.Key_Delete:
            # Do nothing if the cell is empty
            if not self.highlight_selected[0] and len(self.mass_highlight) < 1:
                return

            if len(self.mass_highlight) > 1:
                for highlight, index in self.mass_highlight:
                    grid_manager.remove_from_grid(self.app, index, True)
                return

            grid_manager.remove_from_grid(
                self.app, self.highlight_selected[1], True)

    def scene_changed(self):
        if not self.scene_changed_disconnected:
            if self.highlight_selected[1] is not None:
                self.update()

                image_manipulation.zoom(self.app, grid_manager.get_image_at(
                    self.app,
                    self.highlight_selected[1]))

                if self.highlight_selected[1] in self.app.weapons:
                    image_manipulation.zoom(self.app,
                                            grid_manager.get_weapon_layer(
                                                self.app,
                                                self.highlight_selected[1])[0],
                                            grid_manager.get_weapon_layer(
                                                self.app,
                                                self.highlight_selected[1])[1],
                                            False)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            # Perform horizontal scrolling
            scroll_value = event.angleDelta().y()
            horizontal_scroll_value = scroll_value
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - horizontal_scroll_value)

        if event.modifiers() == Qt.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor

            # Zoom factor
            if event.angleDelta().y() > 0:
                self.zoom_factor *= zoom_in_factor
            else:
                self.zoom_factor *= zoom_out_factor

            # Clamp zoom factor
            self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))

            # self.apply zoom
            self.setTransform(QTransform().scale(
                self.zoom_factor, self.zoom_factor))

        else:
            # Perform regular vertical scrolling
            super().wheelEvent(event)

    def drawBackground(self, painter, rect):
        # Override the drawBackground method to draw only the visible portion

        # Get the visible rectangle of the viewport
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()

        # Set the clipping region to the visible rectangle
        painter.setClipRect(rect.intersected(visible_rect))

        # Call the base implementation to draw the background
        super().drawBackground(painter, rect)


class ZoomView(QGraphicsView):
    def __init__(self, scene):
        super().__init__()

        self.setMinimumSize(300, 300)
        self.setMaximumSize(300, 300)

        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
