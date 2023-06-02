#================================================================================#
# File: main.py
# Created Date: 22-05-2023 | 08:42:24
# Author: Hereiti
#================================================================================
# Last Modified: 02-06-2023 | 10:50:25
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Imports
#================================================================================#
import subprocess
import sys

#================================================================================#
# Third-Party Imports
#================================================================================#
from PySide6.QtWidgets import QApplication, QStyleFactory

#================================================================================#
# Local Application Imports
#================================================================================#
from classes.MainWindow import MainWindow
from modules import config
from modules import miscellaneous

#================================================================================#
# Functions
#================================================================================#
def restart():
    """
    Restarts the application.
    """
    # Quit the current application instance
    QApplication.quit()
    # Launch a new instance of the application
    subprocess.Popen([sys.executable, __file__])

if __name__ == "__main__":
    # Check the configuration
    config.check_config()

    # Create an instance of QApplication
    app = QApplication(sys.argv)
    # Set the application style to Fusion
    app.setStyle(QStyleFactory.create("Fusion"))

    # Create an instance of MainWindow
    window = MainWindow()

    # Connect the aboutToQuit signal of the application to delete_temp_files function
    app.aboutToQuit.connect(lambda: miscellaneous.delete_temp_files(window))
    # Start the application event loop
    app.exec()
