#================================================================================#
# File: graphics_item.py
# Created Date: 05-06-2023 | 16:38:24
# Author: Hereiti
#================================================================================
# Last Modified: 05-06-2023 | 18:35:23
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Third-party imports
#================================================================================#
from PySide6.QtCore import QLineF, QRectF, QTimer
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsItem

#================================================================================#
# Classes
#================================================================================#
class Grid(QGraphicsItem):
    """
    A class representing a grid item in QGraphicsScene.

    Args:
        - cell_size (int): The size of each cell in the grid.
        - columns (int): The number of columns in the grid.
        - rows (int): The number of rows in the grid.
    """
    def __init__(self, columns: int, rows: int, cell_size: int) -> None:
        """Initialize the Grid object."""
        super().__init__()

        self.cell_size = cell_size
        self.columns = columns
        self.rows = rows

        # Place the grid on top of other items
        self.setZValue(2)

    def boundingRect(self) -> QRectF:
        """
        Return the bounding rectangle of the grid

        Returns:
            - The bounding rect of the grid
        """
        return QRectF(0, 0, self.columns * self.cell_size, self.rows * self.cell_size)

    def paint(self, _painter, _option, _widget) -> None:
        """
        Paint the grid.

        Args:
            - painter: The QPainter object used for painting.
            - option: The QStyleOptionGraphicsItem object.
            - widget: The widget being painted on.
        """
        _pen = QPen(QColor(0, 0, 0))
        _painter.setPen(_pen)

        # Draw vertical lines
        for _x in range(self.columns + 1):
            _line = QLineF(_x * self.cell_size, 0, _x * self.cell_size, self.rows * self.cell_size)
            _painter.drawLine(_line)

        for _y in range(self.rows + 1):
            _line = QLineF(0, _y * self.cell_size, self.columns * self.cell_size, _y * self.cell_size)
            _painter.drawLine(_line)

class Highlight(QGraphicsItem):
    """
    A class representing a highlight item in QGraphicsScene.

    Args:
        - color: The color of the highlight.
    """
    def __init__(self, color, cell_size) -> None:
        """Initialize the highlight object"""
        super().__init__()

        # Create attributes for the highlight
        self.color = color
        self.visible = True
        self.cell_size = cell_size

        # Start a timer for a blinking effect
        self.timer = QTimer()
        self.timer.timeout.connect(self.blink)
        self.timer.start(500)

    def boundingRect(self) -> QRectF:
        """
        Return the bounding rect of the highlight

        Returns:
            - The bounding rect of the highlight
        """
        return QRectF(0, 0, self.cell_size, self.cell_size)

    def paint(self, painter, option, widget) -> None:
        """
        Paint the highlight.

        Args:
            - painter: The QPainter object used for painting.
            - option: The QStyleOptionGraphicsItem object.
            - widget: The widget being passed on.
        """
        if self.visible:
            painter.setPen(QPen(QColor(self.color), 0))
            painter.setBrush(QBrush(QColor(self.color)))
            painter.drawRect(self.boundingRect())

    def blink(self) -> None:
        """Toggle the visibility of the highlight and trigger an update."""
        self.visible = not self.visible
        self.update()