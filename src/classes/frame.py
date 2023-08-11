#!/usr/bin/env python
"""frame.py"""
from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Qt


class FloatingFrame(QFrame):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.Tool)
        self.setWindowTitle(text)
        self.setMaximumSize(200, 200)
        self.text = text

    def closeEvent(self, event):
        try:
            self.parent().adjustment_toolbar_actions[self.text].setChecked(
                False)
        except Exception:
            super().closeEvent(event)
        super().closeEvent(event)
