#================================================================================#
# File: GraphicsView.py
# Created Date: 22-05-2023 | 10:12:31
# Author: Hereiti
#================================================================================
# Last Modified: 02-06-2023 | 10:52:24
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Imports
#================================================================================#
from typing import Optional, Union, Tuple, List

#================================================================================#
# Third-Party Imports
#================================================================================#
from PySide6.QtCore import QPointF, Qt, QRectF
from PySide6.QtGui import QKeyEvent, QMouseEvent, QImage, QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsPixmapItem, QGraphicsScene

#================================================================================#
# Local Application Imports
#================================================================================#
from classes.GraphcisItem import Grid, Highlight
from modules import edits, icons, images, maths, utils

#================================================================================#
# Classes
#================================================================================#
class GraphicsView(QGraphicsView):
    """
    Custom QGraphicsView subclass for handling graphics interactions.
    """

    def __init__(self, parent=None) -> None:
        """
        Custom GraphicsView class for handling mouse events and displaying graphics items.
        """
        super().__init__(parent)

        # Initialize attributes
        self.highlight_selected: Optional[Union[Highlight, Tuple[int, int]]] = None
        self.highlight_dragging: Optional[Highlight] = None
        self.dragged_item: Optional[QGraphicsPixmapItem] = None
        self.indexes: Optional[List[Tuple[int, int]]] = [None, None]
        self._cell_size = maths.cell_size()

        # Create the scene
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, maths.grid_col() * self._cell_size, maths.grid_row() * self._cell_size + 2)
        self.setSceneRect(-2, -2, maths.grid_col() * self._cell_size + 6, self.scene.height() + 2)
        self.setScene(self.scene)

        # Draw the grid
        self.grid = Grid(maths.grid_col(), maths.grid_row())
        self.scene.addItem(self.grid)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Reimplemented wheel event handler for smooth scrolling.

        Args:
            event (QWheelEvent): The wheel event object.

        """
        delta = event.angleDelta().y()
        modifiers = event.modifiers()

        # Smooth scrolling for vertical movement
        if delta != 0 and not modifiers == Qt.KeyboardModifier.ControlModifier:
            # Adjust the scroll speed as needed
            scroll_amount = maths.cell_size() if delta < 0 else -maths.cell_size()
            scroll_value = self.verticalScrollBar().value() + scroll_amount
            self.verticalScrollBar().setValue(scroll_value)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press event.
        """
        _icons = self.parent().icons

        if event.button() == Qt.MouseButton.LeftButton:
            utils.click_cell(event, self.parent())

        elif event.button() == Qt.MouseButton.RightButton:
            if _icons:
                # Map the mouse cursor position to the scene coordinates
                scene_pos = self.mapToScene(event.pos())

                # Extract the x and y coordinates from the scene position
                _x, _y = scene_pos.x(), scene_pos.y()

                # Get the cell index and origin
                _index = maths.index(int(_x), int(_y))
                _origin = maths.origin(*_index)

                # Create a Highlight and place it at the clicked cell
                self.highlight_dragging = Highlight("green")
                self.highlight_dragging.setPos(QPointF(*_origin))
                self.scene.addItem(self.highlight_dragging)

                # Create a QRectF representing the clicked cell
                cell_rect = QRectF(*_origin, self._cell_size, self._cell_size)

                _item: Optional[QGraphicsPixmapItem] = None

                # Check for collision between the item and the Highlight
                for item in self.scene.items(cell_rect):
                    if isinstance(item, QGraphicsPixmapItem):
                        if item.collidesWithItem(self.highlight_dragging):
                            _item = item

                if _item is not None:
                    # Store the dragged item and its initial cell index
                    _item.setZValue(1)
                    self.dragged_item = _item
                    self.indexes[0] = tuple(_index)

        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move event.
        """
        if self.dragged_item and self.indexes:
            # Map the mouse cursor position to the scene coordinates
            scene_pos = self.mapToScene(event.pos())
            _x, _y = scene_pos.x(), scene_pos.y()

            # Get the current cell index and clamp it within the grid bounds
            _index = maths.index(int(_x), int(_y))
            _index = (
                min(max(_index[0], 0), maths.grid_col() - 1),
                min(max(_index[1], 0), maths.grid_row() - 1)
            )

            # Calculate the origin of the current cell
            _origin: Tuple[int, int] = maths.origin(*_index)

            # Move the dragged item and highlight to the current cell
            self.dragged_item.setPos(QPointF(*_origin))
            self.highlight_dragging.setPos(QPointF(*_origin))

            # Create a QRectF representing the current cell
            cell_rect = QRectF(*_origin, self._cell_size, self._cell_size)
            _item: Optional[QGraphicsPixmapItem] = None

            # Check for collision between other items and the highlight
            for item in self.scene.items(cell_rect):
                if isinstance(item, QGraphicsPixmapItem) and item != self.dragged_item:
                    if item.collidesWithItem(self.highlight_dragging):
                        item.setOpacity(0.5)
                        _item = item

            # Reset opacity for other items in the scene
            for item in self.scene.items():
                if isinstance(item, QGraphicsPixmapItem):
                    item.setOpacity(1.0)

            # Update the current cell index
            self.indexes[1] = tuple(_index)

            # Update the zoom scene based on the collision result
            images.zoom(self.parent(), _item)

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse release event.
        """
        _icons = self.parent().icons

        if event.button() == Qt.MouseButton.RightButton:
            if self.highlight_dragging is not None:
                # Remove the highlight item from the scene
                self.scene.removeItem(self.highlight_dragging)
                self.highlight_dragging = None

            if self.dragged_item is not None:
                if len(self.indexes) != 2 or self.indexes[0] == self.indexes[1]:
                    # Reset dragged item and indexes if not a valid move
                    self.dragged_item = None
                    self.indexes = [None, None]
                    return

                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    # Handle item switch with Shift key modifier
                    item_a: Optional[QGraphicsPixmapItem] = _icons.get(self.indexes[0])
                    item_b: Optional[QGraphicsPixmapItem] = _icons.get(self.indexes[1])
                    origin_a: Tuple[int, int] = maths.origin(*self.indexes[0])
                    origin_b: Tuple[int, int] = maths.origin(*self.indexes[1])

                    if item_a is not None:
                        item_a.setPos(QPointF(*origin_b))
                        _icons[self.indexes[1]] = item_a

                    if item_b is not None:
                        item_b.setPos(QPointF(*origin_a))
                        item_b.setOpacity(1.0)
                        _icons[self.indexes[0]] = item_b

                    edits.history(self.parent(), "MOVE", (self.indexes), None, "SWITCH")

                else:
                    # Handle item move/overwrite without Shift key modifier
                    temp_path = None
                    if self.indexes[1] in _icons:
                        temp_path = icons.remove(self.parent(), self.indexes[1])

                    item: Optional[QGraphicsPixmapItem] = _icons.get(self.indexes[0])
                    if item:
                        item.setPos(*maths.origin(*self.indexes[1]))
                        _icons[self.indexes[1]] = self.dragged_item
                        del _icons[self.indexes[0]]

                    edits.history(self.parent(), "MOVE", (self.indexes), temp_path, "OVERWRITE")

                # Reset dragged item and indexes
                self.dragged_item = None
                self.indexes = [None, None]

                # Zoom the scene based on the selected item or no selection
                if self.highlight_selected and isinstance(self.highlight_selected, list):
                    images.zoom(self.parent(), images.image_at(self.parent(), self.highlight_selected[1]))
                else:
                    images.zoom(self.parent(), None)

        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse double-click event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Select an image file and add it to the scene
            image: QImage = icons.select_file(self.parent())

            if image:
                icons.add(self.parent(), image, self.highlight_selected[1])

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handle key press event.
        """
        if event.key() == Qt.Key.Key_Delete:
            if not self.highlight_selected:
                return

            icons.remove(self.parent(), self.highlight_selected[1], True)
