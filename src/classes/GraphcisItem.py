#================================================================================#
# File: GraphicsItem.py
# Created Date: 22-05-2023 | 10:25:04
# Author: Hereiti
#================================================================================
# Last Modified: 02-06-2023 | 10:51:17
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Third-Party Imports
#================================================================================#
from PySide6.QtCore    import QLineF, QRectF, QTimer
from PySide6.QtGui     import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsItem

#================================================================================#
# Local Application Imports
#================================================================================#
from modules.maths import cell_size

#================================================================================#
# Classes
#================================================================================#
class Grid(QGraphicsItem):
    """
    A class representing a grid item in QGraphicsScene.

    Args:
        columns (int): The number of columns in the grid.
        rows (int): The number of rows in the grid.

    Attributes:
        columns (int): The number of columns in the grid.
        rows (int): The number of rows in the grid.
        cell_size: The size of each cell in the grid.
    
    Methods:
        boundingRect(): Return the bounding rectangle of the grid.
        paint(painter, option, widget): Paint the grid.

    """
    def __init__(self, columns: int, rows: int) -> None:
        """
        Initialize the Grid object.

        Args:
            columns: The number of columns in the grid.
            rows: The number of rows in the grid.
        """
        super().__init__()

        self.columns = columns
        self.rows = rows

        # Calculate the cell size based on the grid size
        self.cell_size = cell_size()

        self.setZValue(+2)

    def boundingRect(self) -> QRectF:
        """
        Return the bounding rectangle of the grid.

        Returns:
            The bounding rectangle of the grid.
        """
        return QRectF(0, 0, self.columns * self.cell_size, self.rows * self.cell_size)

    def paint(self, painter, option, widget) -> None:
        """
        Paint the grid.

        Args:
            painter: The QPainter object used for painting.
            option: The QStyleOptionGraphicsItem object.
            widget: The widget being painted on.
        """
        pen = QPen(QColor(0, 0, 0))
        painter.setPen(pen)

        # Draw vertical lines
        for _x in range(self.columns + 1):
            line = QLineF(_x * self.cell_size, 0, _x * self.cell_size, self.rows * self.cell_size)
            painter.drawLine(line)

        # Draw horizontal lines
        for _y in range(self.rows + 1):
            line = QLineF(0, _y * self.cell_size, self.columns * self.cell_size, _y * self.cell_size)
            painter.drawLine(line)

class Highlight(QGraphicsItem):
    """
    A class representing a highlight item in QGraphicsScene.

    Args:
        color: The color of the highlight.

    Attributes:
        color (str): The color of the highlight.
        visible (bool): Flag indicating the visibility of the highlight.
        timer (QTimer): QTimer object used to control the visibility of the highlight.

    Methods:
        boundingRect(): Return the bounding rectangle of the highlight.
        paint(painter, option, widget): Paint the highlight.
        blink(): Toggle the visibility of the highlight and trigger an update.
    """
    def __init__(self, color: str) -> None:
        """
        Initialize the Highlight object.

        Args:
            color: The color of the highlight.
        """
        super().__init__()

        self.color = color

        self.visible = True

        # Start a timer to control the visibility of the highlight
        self.timer = QTimer()
        self.timer.timeout.connect(self.blink)
        self.timer.start(500)

    def boundingRect(self) -> QRectF:
        """
        Return the bounding rectangle of the highlight.

        Returns:
            The bounding rectangle of the highlight.
        """
        _cell_size = cell_size()
        return QRectF(0, 0, _cell_size, _cell_size)

    def paint(self, painter, option, widget) -> None:
        """
        Paint the highlight.

        Args:
            painter: The QPainter object used for painting.
            option: The QStyleOptionGraphicsItem object.
            widget: The widget being painted on.
        """
        if self.visible:
            painter.setPen(QPen(QColor(self.color), 0))
            painter.setBrush(QBrush(QColor(self.color)))
            painter.drawRect(self.boundingRect())

    def blink(self) -> None:
        """
        Toggle the visibility of the highlight and trigger an update.

        Returns:
            None
        """
        self.visible = not self.visible
        self.update()
