#!/usr/bin/env python
"""item_highlight.py"""
from PySide6.QtCore import QRect, QTimer
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsItem


class Highlight(QGraphicsItem):
    """
    A class representing a highlight item in QGraphicsScene.

    Args:
        - color: The color of the highlight.
    """

    def __init__(self, color, cell_width, cell_height):
        """Initialize the highlight object"""
        super().__init__()

        # Create attributes for the highlight
        self.color = color
        self.visible = True
        self.cell_width = cell_width
        self.cell_height = cell_height

        # Start a timer for a blinking effect
        self.timer = QTimer()
        self.timer.timeout.connect(self.blink)
        self.timer.start(500)

    def reset_timer(self):
        """Reset the timer"""
        self.timer.stop()
        self.visible = True
        self.update()
        self.timer.start(500)

    def boundingRect(self):
        """
        Return the bounding rect of the highlight

        Returns:
            - The bounding rect of the highlight
        """
        return QRect(0, 0, self.cell_width, self.cell_height)

    def paint(self, painter, option, widget):
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

    def blink(self):
        """Toggle the visibility of the highlight and trigger an update."""
        self.visible = not self.visible
        self.update()
