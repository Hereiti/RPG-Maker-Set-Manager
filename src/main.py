#!/usr/bin/env python
"""
RPG Maker - Set Manager

This script is the entrypoint for the RPG Maker Set Manager application.
It allows users to manage sets of resources for RPG Maker projects.

Usage:
    python main.py [options]

Options:g
    -h, --help       Show this help message and exit
    -v, --version    Show this software version
    --debug          Enable debug mode

Dependencies:
    - Python 3.11 or above
    - PySide6 6.5.1.1

Please refer to the documentation for more information.
"""
import argparse
import os
import sys
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QStyleFactory
from classes.main_window import MainWindow
from modules import config
from modules import misc
from modules import utils


load_dotenv()


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: An object containing parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="RPG Maker - Set Manager")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"RPG Maker - Set Manager v{os.getenv('VERSION')}"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    return parser.parse_args()


def main():
    """
    Main function for executing the program.

    This function serves as the entry point of the program and is responsible for
    coordinating the execution of various tasks and functions.

    Returns:
        None
    """
    # parse command-line arguments
    parse_arguments()


def restart():
    """Restart the program."""
    # Quit the current application
    QApplication.quit()

    # Launch a new instance with
    python_executable = sys.executable
    script_path = os.path.abspath(__file__)
    arguments = sys.argv[1:]
    os.execv(python_executable, [
        '"{}"'.format(python_executable),
        '"{}"'.format(script_path)] + arguments
    )


if __name__ == "__main__":
    # Ensure that the config exists
    config.ensure_config()

    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Current application version
    current_version = f"v{os.getenv('VERSION')}-alpha"
    utils.compare_versions(current_version)

    # Set the application style
    app.setStyle(QStyleFactory.create("Fusion"))

    # Create an instance of MainWindow
    window = MainWindow()

    sys.excepthook = utils.exception_handler

    # Connect the aboutToQuit signal
    app.aboutToQuit.connect(lambda: misc.delete_temp_files(window))

    # Start the application event loop
    app.exec()
