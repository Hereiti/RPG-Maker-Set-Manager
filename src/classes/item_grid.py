#!/usr/bin/env python
"""item_grid.py"""
from PySide6.QtCore import QLine, QRect, Qt
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QGraphicsItem


class Grid(QGraphicsItem):
    """
    A class representing a grid item in QGraphicsScene.

    Args:
        - cell_width (int): The width of each cell in the grid.
        - cell_height (int): The height of each cell in the grid.
        - columns (int): The number of columns in the grid.
        - rows (int): The number of rows in the grid.

    Methods:
        boundingRect: Returns the bounding rectangle of the grid
        paint: Paint the item
    """

    def __init__(self, columns, rows, cell_width, cell_height):
        "Initialize the Grid object."
        super().__init__()

        self.cell_width = cell_width
        self.cell_height = cell_height
        self.columns = columns
        self.rows = rows

        # Place the grid on top of other item
        self.setZValue(2)

    def boundingRect(self):
        """
        Return the bounding rectangle of the grid.

        Returns:
            - The bounding rect of the grid.
        """
        return QRect(0, 0, self.columns * self.cell_width, self.rows * self.cell_height)

    def paint(self, painter, option, widget):
        """
        Paint the grid.

        Args:
            - painter: The QPainter object used for painting.
            - option: The QStyleOptionGraphicsItem object.
            - widget: The widget being painted on.
        """
        pen = QPen(Qt.GlobalColor.black)
        painter.setPen(pen)

        # Draw vertical lines
        for x in range(self.columns + 1):
            line = QLine(x * self.cell_width, 0, x *
                         self.cell_width, self.rows * self.cell_height)
            painter.drawLine(line)

        # Draw horizontal lines
        for y in range(self.rows + 1):
            line = QLine(0, y * self.cell_height, self.columns *
                         self.cell_width, y * self.cell_height)
            painter.drawLine(line)
