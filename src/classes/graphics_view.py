#================================================================================#
# File: graphics_view.py
# Created Date: 05-06-2023 | 11:28:10
# Author: Hereiti
#================================================================================
# Last Modified: 08-06-2023 | 12:12:03
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
from typing import List, Optional, Tuple

#================================================================================#
# Third-party imports
#================================================================================#
from PySide6.QtCore import QMimeData, QPointF, QRectF, Qt
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QImage, QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

#================================================================================#
# Local imports
#================================================================================#
from classes.graphics_item import Grid, Highlight

from modules import edits
from modules import icons
from modules import images
from modules import maths
from modules import utils

#================================================================================#
# Classes
#================================================================================#
class GraphicsView(QGraphicsView):
    """Custom QGraphicsView subclass for handling graphics interactions."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # Initialize attributes
        self.highlight_selected = (None, None)
        self.cell_size = self.parent().cell_size

        # Initialize attributes for the drag event
        self.drag_item = None
        self.drag_highlight = None
        self.drag_indexes = [None, None]

        # Create the scene
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, maths.grid_col() * self.cell_size, maths.grid_row() * self.cell_size)
        self.setSceneRect(-2, -2, maths.grid_col() * self.cell_size + 6, maths.grid_row() * self.cell_size + 2)
        self.setScene(self.scene)

        # Draw the grid
        self.grid = Grid(maths.grid_col(), maths.grid_row(), self.cell_size)
        self.scene.addItem(self.grid)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.parent().thread_running:
            return

        """Handles mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            utils.click_cell(event, self.parent())

        if event.button() == Qt.MouseButton.RightButton:
            if not self.parent().images:
                return

            # Map the mouse cursor position to the scene coordinates
            _scene_pos = self.mapToScene(event.pos())
            _x, _y = _scene_pos.x(), _scene_pos.y()

            # Get the cell index and origin
            _index = maths.index(_x, _y)
            _origin = maths.origin(_index)

            # Create a highlight and place it at the clicked cell
            self.drag_highlight = Highlight("red", self.cell_size)
            self.drag_highlight.setPos(*_origin)
            self.scene.addItem(self.drag_highlight)

            # Create a QRectF representing the clicked cell
            _cell_rect = QRectF(*_origin, self.cell_size, self.cell_size)

            # Check for collision between the highlight and other items
            _item = None
            for item in self.scene.items(_cell_rect):
                if isinstance(item, QGraphicsPixmapItem):
                    if item.collidesWithItem(self.drag_highlight):
                        _item = item
                        break

            if _item is not None:
                # Store the item and its initial index
                _item.setZValue(1)
                self.drag_item = _item
                self.drag_indexes[0] = _index

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.parent().thread_running:
            return

        """Handles mouse move event."""
        if self.drag_item and self.drag_indexes[0]:
            if self.parent().animation[0]:
                images.stop_animations(self.parent())

            if not self.drag_highlight:
                return

            # Map the mouse cursor position to the scene coordinates
            _scene_pos = self.mapToScene(event.pos())
            _x, _y = _scene_pos.x(), _scene_pos.y()

            # Get the current cell index and clamp it within the grid bounds
            _index = maths.index(int(_x), int(_y))
            _index = (
                min(max(_index[0], 0), maths.grid_col() - 1),
                min(max(_index[1], 0), maths.grid_row() - 1)
            )

            # Calculate the origin of the cell
            _origin = maths.origin(_index)

            # Move the item and highlight to the current cell
            self.drag_item.setPos(*_origin)
            self.drag_highlight.setPos(*_origin)

            # Create a QRectF representing the current cell
            _cell_rect = QRectF(*_origin, self.cell_size, self.cell_size)

            # Check for collision between other items and the highlight
            _item = None
            for item in self.scene.items(_cell_rect):
                if isinstance(item, QGraphicsPixmapItem):
                    if item.collidesWithItem(self.drag_highlight) and item != self.drag_item:
                        _item = item
                        break

            # Update the drag_index[1] value to current cell index
            self.drag_indexes[1] = _index

            # Update the zoom scene based on the collision result
            images.zoom(self.parent(), _item)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.parent().thread_running:
            return

        """Handle mouse release event."""
        if event.button() == Qt.MouseButton.RightButton:
            if self.drag_highlight is not None:
                # Remove the highlight from the scene
                self.scene.removeItem(self.drag_highlight)
                self.drag_highlight = None

            if all(index is not None for index in self.drag_indexes):
                if self.drag_indexes[0] == self.drag_indexes[1]:
                    # Reset drag_item if and drag_indexes
                    self.drag_indexes = [None, None]
                    self.drag_item = None
                    return

                _images = self.parent().images
                _index_a, _index_b = self.drag_indexes

                # Checks if the shift key is held down for item switching
                if event.modifiers() and Qt.KeyboardModifier.ShiftModifier:
                    _item_a = _images.get(_index_a)
                    _item_b = _images.get(_index_b)

                    _origin_a = maths.origin(_index_a)
                    _origin_b = maths.origin(_index_b)

                    if _item_a:
                        _item_a.setPos(*_origin_b)
                        _images[_index_b] = _item_a

                    if _item_b:
                        _item_b.setPos(*_origin_a)
                        _images[_index_a] = _item_b

                    edits.history(self.parent(), "MOVE", self.drag_indexes, None, "SWITCH")

                else:
                    # Simply overwrite the new cell
                    _temp_path = None
                    if _index_b in _images:
                        _temp_path = icons.remove(self.parent(), _index_b)

                    self.drag_item.setPos(*maths.origin(_index_b))
                    _images[_index_b] = self.drag_item
                    del _images[_index_a]

                    edits.history(self.parent(), "MOVE", self.drag_indexes, _temp_path, "OVERWRITE")

                # Reset attributes
                self.drag_item = None
                self.drag_indexes = [None, None]

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.parent().thread_running:
            return

        """Handles mouse double-click event."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Prompt for an image file
            _image = utils.prompt_file(self.parent())

            if _image:
                icons.add(self.parent(), _image, self.highlight_selected[1])

    def dragEnterEvent(self, event: QDragEnterEvent):
        if self.parent().thread_running:
            return

        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if self.parent().thread_running:
            return

        # Map the event position to scene coordinates
        _scene_pos = self.mapToScene(event.pos())
        _x, _y = _scene_pos.x(), _scene_pos.y()

        # Calculate the cell index and origin
        _cell_index = maths.index(_x, _y)
        _cell_origin = maths.origin(_cell_index)

        # Check if the click is out of bounds
        _limit = maths.origin((maths.grid_col() - 1, maths.grid_row() - 1))
        if any(_coord < 0 or _coord > limit for _coord, limit, in zip(_cell_origin, _limit)):
            return

        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile() and url.toLocalFile().endswith('.png'):
                    # Call your function with the dropped image file path
                    image = QImage(url.toLocalFile())

                    if image.width() <= maths.cell_size() and image.height() <= maths.cell_size():
                        # Map the mouse cursor position to the scene coordinates
                        scene_pos = self.mapToScene(event.pos())
                        _x, _y = scene_pos.x(), scene_pos.y()

                        # Get the current cell index and clamp it within the grid bounds
                        _index = maths.index(int(_x), int(_y))

                        icons.add(self.parent(), image, _index)
                    else:
                        # Map the mouse cursor position to the scene coordinates
                        scene_pos = self.mapToScene(event.pos())
                        _x, _y = scene_pos.x(), scene_pos.y()

                        # Get the current cell index and clamp it within the grid bounds
                        _index = maths.index(int(_x), int(_y))
                        icons.load(self.parent(), image, True, False, _index)
                    break

    def dragMoveEvent(self, event: QDragMoveEvent):
        if self.parent().thread_running:
            return

        event.acceptProposedAction()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press event."""
        if event.key() == Qt.Key.Key_Delete:
            if not self.highlight_selected[0]:
                return

            icons.remove(self.parent(), self.highlight_selected[1], True)