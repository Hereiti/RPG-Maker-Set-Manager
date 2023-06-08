#================================================================================#
# File: main.py
# Created Date: 05-06-2023 | 10:24:19
# Author: Hereiti
#================================================================================
# Last Modified: 07-06-2023 | 18:01:17
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
import os
import sys

#================================================================================#
# Third-party imports
#================================================================================#
from PySide6.QtWidgets import QApplication, QStyleFactory

#================================================================================#
# Local imports
#================================================================================#
from classes.main_window import MainWindow

from modules import config
from modules import misc

#================================================================================#
# Functions
#================================================================================#
def restart():
    """Restarts the application."""
    # Quit the current application instance
    QApplication.quit()

    # Launch a new instance with the same command-line arguments
    python_executable = sys.executable
    script_path = os.path.abspath(__file__)
    arguments = sys.argv[1:]  # Exclude the script name itself
    os.execv(python_executable, ['"{}"'.format(python_executable), '"{}"'.format(script_path)] + arguments)

if __name__ == "__main__":
    # Ensure that the config file exists
    config.ensure_config()

    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Set the application style
    app.setStyle(QStyleFactory.create("Fusion"))

    # Create an instance of MainWindow
    window = MainWindow()

    # Connect the aboutToQuit signal
    app.aboutToQuit.connect(lambda: misc.delete_temp_files(window))
    # Start the application event loop
    app.exec()
