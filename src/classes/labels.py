#!/usr/bin/env python
"""label_round.py"""
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import (
    QBrush, QColor, QFontMetrics, QPainter, QPainterPath, QPen
)
from PySide6.QtWidgets import QLabel


class RoundLabel(QLabel):
    """
    This class extends QLabel to create a round-shaped label.

    Args:
        - width (int): The width of the button.
        - height (int): The height of the button.
        - parent (QWidget, optinal): The parent widget. Defaults to None.
    """

    def __init__(self, width, height, parent=None):
        """Initialize the label"""
        super().__init__(parent)

        # Set label parameters
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        """Paint event handler"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create a path for the label shape
        path = QPainterPath()
        path.addEllipse(1, 1, self.width() - 2, self.height() - 2)

        # Set the button background and border color
        painter.fillPath(path, QBrush(QColor("#2e2e2e")))
        painter.setPen(QPen(QColor("#545454")))
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)

        # Set the color and font for the button text
        font = self.font()
        font.setPointSize(20)
        painter.setPen(QColor(Qt.GlobalColor.white))
        painter.setFont(font)

        # Calculate the text rectangle and clip the text if needed
        rect = QRect(0, 0, self.width(), self.height()).adjusted(5, 0, 5, 0)
        metrics = QFontMetrics(font)
        text = metrics.elidedText(
            self.text(), Qt.TextElideMode.ElideRight, rect.width())

        # Draw the text at the center of the label
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
