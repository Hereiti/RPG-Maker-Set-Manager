#!/usr/bin/env python
"""dialog_forms.py"""
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QLineEdit, QMessageBox, QPushButton,
    QTextEdit, QVBoxLayout
)


class Form(QDialog):
    """A form using a QDialog"""

    def __init__(self, parent=None):
        """
        Initialize the form

        Args:
            - parent: The parent widget of this one
        """
        super().__init__(parent)
        self.setWindowTitle("Report Issue")

        layout = QVBoxLayout(self)

        # Add a label and line edit for a single-line input
        label = QLabel("Enter a Title:")
        layout.addWidget(label)
        self.title = QLineEdit()
        layout.addWidget(self.title)

        # Add a label and text edit for a multi-line input
        label = QLabel(
            "Describes your problem with as much details as possible:")
        layout.addWidget(label)
        self.desc = QTextEdit()
        layout.addWidget(self.desc)

        label = QLabel(
            "Any abuses of this feature will lead to it being disabled.")
        layout.addWidget(label)

        # Add OK and Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_button_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept_button_clicked(self):
        # Validate the fields before accepting the dialog
        if self.title.text().strip() == "":
            QMessageBox.warning(self, "Error", "Title field cannot be empty.")
            return

        if self.desc.toPlainText().strip() == "":
            QMessageBox.warning(
                self, "Error", "Description field cannot be empty.")
            return

        # Accept the dialog
        self.accept()


class TwoInputs(QDialog):
    """Allows the user to input two differents values in the same dialog"""

    def __init__(
            self, parent=None, title="",
            label_1="label 1", value_1="0",
            label_2="label 2", value_2="0"):
        """Initialize the dialog"""
        super().__init__()
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()

        # First text box
        self.label_1 = QLabel(label_1)
        self.textbox_1 = QLineEdit(value_1)
        self.label_2 = QLabel(label_2)
        self.textbox_2 = QLineEdit(value_2)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        self.widgets = [self.label_1, self.textbox_1,
                        self.label_2, self.textbox_2, self.ok_button]

        for widget in self.widgets:
            self.layout.addWidget(widget)

        self.setLayout(self.layout)


class FourInputs(QDialog):
    """Allows the user to input four differents values in the same dialog"""

    def __init__(
            self, parent=None, title="",
            label_1="label 1", value_1="0",
            label_2="label 2", value_2="0",
            label_3="label 3", value_3="0",
            label_4="label 4", value_4="0"):
        """Initialize the dialog"""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()

        # First text box
        self.label_1 = QLabel(label_1)
        self.textbox_1 = QLineEdit(value_1)
        self.label_2 = QLabel(label_2)
        self.textbox_2 = QLineEdit(value_2)
        self.label_3 = QLabel(label_3)
        self.textbox_3 = QLineEdit(value_3)
        self.label_4 = QLabel(label_4)
        self.textbox_4 = QLineEdit(value_4)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        self.widgets = [self.label_1, self.textbox_1,
                        self.label_2, self.textbox_2,
                        self.label_3, self.textbox_3,
                        self.label_4, self.textbox_4,
                        self.ok_button]

        for widget in self.widgets:
            self.layout.addWidget(widget)

        self.setLayout(self.layout)
