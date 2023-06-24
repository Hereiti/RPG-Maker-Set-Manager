#!/usr/bin/env python
"""graphics_view.py"""
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
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
        self.highlight_selected = (None, None)
        self.cell_width, self.cell_height = self.parent().cell_size

        # Initialize more attributes for the drag event
        self.drag_item = None
        self.drag_highlight = None
        self.drag_indexes = [None, None]

        self.scene_changed_disconnected = False

        # Create a scene
        self.scene = QGraphicsScene()
        width = maths.grid_col() * self.cell_width
        height = maths.grid_row() * self.cell_height
        self.scene.setSceneRect(0, 0, width, height)
        self.setSceneRect(-3, -1, width + 5, height + 2)
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
        if self.parent().thread_running:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            grid_manager.click_cell(event, self.parent())

        if event.button() == Qt.MouseButton.RightButton:
            self.scene_changed_disconnected = True

            # Return if there is no image loaded
            if not self.parent().images:
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
                        if item in self.parent().images.values():
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
        if self.parent().thread_running:
            return

        if self.drag_item and self.drag_indexes[0]:
            if self.parent().animation[0]:
                image_manipulation.stop_animations[self.parent()]

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
                        if item in self.parent().images.values():
                            if item != self.drag_item:
                                _item = item
                                _item.setZValue(0)
                                break

            # Update the drag_indexes[1] value to current cell index
            self.drag_indexes[1] = index
            image_manipulation.zoom(
                self.parent(), grid_manager.get_image_at(
                    self.parent(), self.drag_indexes[1]
                ))

    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""
        # Prevent running if a thread is running.
        if self.parent().thread_running:
            return

        # Reconnect the changed event
        self.scene_changed_disconnected = False

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

                images = self.parent().images
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
                        self.parent(), "MOVE", self.drag_indexes, None, "SWITCH")

                else:
                    # Simply overwrite the new cell
                    temp_path = None
                    if index_b in images:
                        temp_path = grid_manager.remove_from_grid(
                            self.parent(), index_b)

                    self.drag_item.setPos(*maths.cell_origin(index_b))
                    images[index_b] = self.drag_item
                    del images[index_a]

                    utils.history(
                        self.parent(), "MOVE",
                        self.drag_indexes, temp_path, "OVERWRITE")

                # Reset attributes
                self.drag_item = None
                self.drag_indexes = [None, None]

    def mouseDoubleClickEvent(self, event):
        """Handles mouse double-click event."""
        # Prevent running if a thread is running
        if self.parent().thread_running:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            # Prompt for an image file
            image = files.prompt_file(self.parent())

            if image:
                grid_manager.add_to_grid(
                    self.parent(), image, self.highlight_selected[1])

    def dropEvent(self, event):
        """Handles the drop event."""
        # Prevent running if a thread is running
        if self.parent().thread_running:
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
                        grid_manager.add_to_grid(self.parent(), image, index)

                    else:
                        # Load the whole image
                        grid_manager.load(
                            self.parent(), image, True, False, index)

    def dragMoveEvent(self, event):
        """Handles drag move event."""
        # Prevent running if a thread is running
        if self.parent().thread_running:
            return

        event.acceptProposedAction()

    def keyPressEvent(self, event):
        """Handles key press event."""
        # Prevent running if a thread is running
        if self.parent().thread_running:
            return

        # Remove the image if the del key is pressed
        if event.key() == Qt.Key.Key_Delete:
            # Do nothing if the cell is empty
            if not self.highlight_selected[0]:
                return

            grid_manager.remove_from_grid(
                self.parent(), self.highlight_selected[1], True)

    def scene_changed(self):
        if not self.scene_changed_disconnected:
            if self.highlight_selected[1] is not None:
                self.update()

                image_manipulation.zoom(self.parent(),
                                        grid_manager.get_image_at(
                    self.parent(),
                    self.highlight_selected[1]))

                if self.highlight_selected[1] in self.parent().layer_1:
                    image_manipulation.zoom(
                        self.parent(),
                        grid_manager.get_layer_1(
                            self.parent(), self.highlight_selected[1])[0],
                        grid_manager.get_layer_1(
                            self.parent(), self.highlight_selected[1])[1],
                        False)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            # Perform horizontal scrolling
            scroll_value = event.angleDelta().y()
            horizontal_scroll_value = scroll_value
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - horizontal_scroll_value)

        else:
            # Perform regular vertical scrolling
            super().wheelEvent(event)
