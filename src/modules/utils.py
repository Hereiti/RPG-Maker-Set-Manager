#!/usr/bin/env python
"""utils.py"""
import os
import re
import sys
import requests
import textwrap
import traceback
from github import Github
from dotenv import load_dotenv
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, qAlpha
from PySide6.QtWidgets import QColorDialog, QDialog, QMessageBox
from classes import main_window
from classes import dialogs
from modules import config

extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS
load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))


def has_valid_pixel(image):
    """
    Checks if the given image has any pixel with alpha higher than 25.

    Args:
        - image: The QImage or QPixmap to check.

    Returns:
        bool: True if the image has at least one pixel with an alpha
            higher than 25, False otherwise
    """
    # Convert the image to a QPixmap
    pixmap = QPixmap(image)

    # Convert the QPixmap to a QImage
    qimage = pixmap.toImage()

    # Iterate over the pixels and check their alpha values
    for y in range(qimage.height()):
        for x in range(qimage.width()):
            pixel = qimage.pixel(x, y)
            alpha = qAlpha(pixel)
            if alpha > 25:
                return True

    return False


def show_popup(message, icon_type, buttons, title=None):
    """
    Display a popup dialog with a message, icon, and buttons.

    This function creates and displays a popup dialog with the specified message, icon,
    and buttons. It returns the text of the button that was clicked by the user.

    Args:
        message (str): The message to display in the popup.
        icon_type (str): The type of the icon to display in the popup.
        buttons (list): The list of button types to display in the popup.

    Returns:
        str: The text of the button that was clicked by the user.
    """
    popup = QMessageBox()

    # Set the icon
    icon_mapping = {
        "WARNING": QMessageBox.Icon.Warning,
        "QUESTION": QMessageBox.Icon.Question,
        "ERROR": QMessageBox.Icon.Critical,
        "INFO": QMessageBox.Icon.Information
    }

    icon = icon_mapping.get(icon_type, QMessageBox.Icon.NoIcon)
    popup.setIcon(icon)

    # Set the window title, message, and buttons
    if title:
        popup.setWindowTitle(title)
    else:
        popup.setWindowTitle(icon_type)

    popup.setWindowFlags(Qt.WindowStaysOnTopHint)
    popup.setTextFormat(Qt.RichText)
    popup.setText(message)
    popup.setStandardButtons(get_buttons(buttons))
    popup.exec()

    return popup.clickedButton().text()


def get_buttons(buttons: list) -> QMessageBox.StandardButton:
    """Get the standard buttons corresponding to the specified button types.

    This function returns the standard buttons object corresponding to the specified
    button types.

    Args:
        buttons (list): The list of button types.

    Returns:
        - QMessageBox.StandardButton: The standard buttons object corresponding to the
            specified button types.
    """
    button_mapping = {
        "OK": QMessageBox.StandardButton.Ok,
        "CANCEL": QMessageBox.StandardButton.Cancel,
        "YES": QMessageBox.StandardButton.Yes,
        "NO": QMessageBox.StandardButton.No,
        "SAVE": QMessageBox.StandardButton.Save,
        "DISCARD": QMessageBox.StandardButton.Discard,
        "CLOSE": QMessageBox.StandardButton.Close,
        "RETRY": QMessageBox.StandardButton.Retry,
        "IGNORE": QMessageBox.StandardButton.Ignore
    }

    # Initialize the standard buttons with NoButton
    standard_buttons = QMessageBox.StandardButton(
        QMessageBox.StandardButton.NoButton)

    # Iterate over the button types and add them to the standard buttons object
    for button in buttons:
        standard_buttons |= button_mapping.get(
            button, QMessageBox.StandardButton.NoButton)

    return standard_buttons


def config_changes_restart(app, key, value, creator=None, opt_value=None):
    """Handle configuration changes and restart the application if necessary.

    This function displays a warning popup to inform the user about potential unsaved
    changes. If the user chooses to continue without saving, it restores the previous
    configuration settings in the menu. Otherwise, it updates the configuration settings
    with the new values and restarts the application.

    Args:
        app: The application main window
        key: The configuration key.
        value: The new configuration value.

    Returns:
        None
    """
    # Show a warning popup to confirm whether to continue without saving.
    response = show_popup(
        "Any unsaved changes will be lost.\nDo you want to continue ?",
        "WARNING", ["YES", "NO"]
    )

    if response == "&No":
        # Restore previous configuration settings in the menu.
        for action in app.view_menu.actions():
            if action.menu():
                for action in action.menu().actions():
                    if action.text() == config.config_get(key):
                        action.setChecked(True)
        return

    # Update the configuration settings with the new values
    config.config_set(key, value)
    parallel_config_changes(key, value, creator, opt_value)

    # Restart the application
    from main import restart
    restart()


def parallel_config_changes(key, value, creator, opt_value):
    if creator is None:
        config.config_set("CREATOR", "None")

        if key == "Tileset Sheet" and value == "A1-A2":
            config.config_set("GRID COLUMNS", "16")
            config.config_set("GRID ROWS", "12")

        if key == "Tileset Sheet" and value == "A3":
            config.config_set("GRID COLUMNS", "16")
            config.config_set("GRID ROWS", "8")

        if key == "Tileset Sheet" and value == "A4":
            config.config_set("GRID COLUMNS", "16")
            config.config_set("GRID ROWS", "15")

        if key == "Tileset Sheet" and value == "A5":
            config.config_set("GRID COLUMNS", "8")
            config.config_set("GRID ROWS", "16")

        if key == "Tileset Sheet" and value == "B-E":
            config.config_set("GRID COLUMNS", "16")
            config.config_set("GRID ROWS", "16")

        if key == "Type" and value == "Icons":
            config.config_set("GRID COLUMNS", "16")
            config.config_set("GRID ROWS", "10000")
            config.config_set("CELL SIZE", "32x32")

        if key == "Type" and value == "Tileset":
            config.config_set("TILESET SHEET", "A1-A2")
            config.config_set("GRID COLUMNS", "16")
            config.config_set("GRID ROWS", "12")
            config.config_set("CELL SIZE", "48x48")

        if key == "Type" and value == "Faces":
            config.config_set("GRID COLUMNS", "4")
            config.config_set("GRID ROWS", "2")
            config.config_set("CELL SIZE", "144x144")

        if key == "Type" and value == "SV Actor":
            config.config_set("GRID COLUMNS", "9")
            config.config_set("GRID ROWS", "6")
            config.config_set("CELL SIZE", "64x64")

        if key == "Type" and value == "Sprites":
            config.config_set("GRID COLUMNS", "12")
            config.config_set("GRID ROWS", "8")
            config.config_set("CELL SIZE", "48x48")

        if key == "Type" and value == "States":
            config.config_set("GRID COLUMNS", "8")
            config.config_set("GRID ROWS", "10")
            config.config_set("CELL SIZE", "96x96")

        if key == "Type" and value == "Weapons":
            config.config_set("GRID COLUMNS", "6")
            config.config_set("GRID ROWS", "6")
            config.config_set("CELL SIZE", "96x64")

        if key == "Type" and value == "Balloons":
            config.config_set("GRID COLUMNS", "8")
            config.config_set("GRID ROWS", "16")
            config.config_set("CELL SIZE", "48x48")

    if creator == "Holder":
        config.config_set("GRID COLUMNS", "4")
        config.config_set("GRID ROWS", "14")
        config.config_set("TYPE", "Holder SV Actors")

        if opt_value == "192x160":
            config.config_set("CELL SIZE", "192x160")
        if opt_value == "160x160":
            config.config_set("CELL SIZE", "160x160")

        config.config_set("CREATOR", "Holder")


def about():
    show_popup(f"""
        <h1>RPG Maker - Set Manager</h1>
        <br>Version : {os.getenv('VERSION')}
        <br>Author  : Costantin Hereiti
        <br>License : <a href="https://www.gnu.org/licenses/lgpl-3.0.en.html">LGPL v3</a>
        <br>Python  : 3.11.3 - 64Bit
        <br>PySide  : 6.5.1
        """, "INFO", ["OK"], "About")  # noqa: E501


def report_issue():
    form = dialogs.Form()

    if form.exec() == QDialog.Accepted:
        title = form.title.text()
        desc = form.desc.toPlainText()

        try:
            # Github Token won't be shared in source code
            # Github repo won't be shared in source code
            github_ = Github(os.getenv('GITHUB_TOKEN'))
            repo = github_.get_repo(os.getenv('GITHUB_REPO'))
            repo.create_issue(title=title, body=desc, labels=["issue"])

        except Exception:
            print(Exception)
            print(textwrap.dedent("""
            This message is here because the github access token wasn't shared in
            the source code.

            You can add your own github repository or remove any references to this
            function.
            """))


def compare_versions(current_version):
    # API endpoint to fetch the releases of a repository
    url = os.getenv('GITHUB_RELEASES')

    if not url:
        return

    try:
        # Send a GET request to the API endpoint
        response = requests.get(url)
        response.raise_for_status()

        # Parse the JSON response
        releases = response.json()

        if releases:
            # Extract the latest release version number
            latest_version = releases[0]['tag_name']

            # Compare the versions
            if current_version < latest_version:
                show_popup(textwrap.dedent("""
                    A new version is available!
                    Get it on <a href="https://hereiti.itch.io/rpg-maker-set-manager">itch.io</a> or <a href="https://github.com/Hereiti/RPG-Maker-Set-Manager/releases">github</a>
                    """), "INFO", ["OK"])  # noqa: E501

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching releases: {e}")


def check_update(current_version):
    # API endpoint to fetch the releases of a repository
    url = os.getenv('GITHUB_RELEASES')

    if not url:
        return

    try:
        # Send a GET request to the API endpoint
        response = requests.get(url)
        response.raise_for_status()

        # Parse the JSON response
        releases = response.json()

        if releases:
            # Extract the latest release version number
            latest_version = releases[0]['tag_name']

            if current_version >= latest_version:
                show_popup(textwrap.dedent("""
                    Your application is up to date.
                    """), "INFO", ["OK"])

            # Compare the versions
            if current_version < latest_version:
                show_popup(textwrap.dedent("""
                    A new version is available!
                    Get it on <a href="https://hereiti.itch.io/rpg-maker-set-manager">itch.io</a> or <a href="https://github.com/Hereiti/RPG-Maker-Set-Manager/releases">github</a>
                    """), "INFO", ["OK"])  # noqa: E501

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching releases: {e}")


def contributors():
    url = os.getenv('GITHUB_URL')

    try:
        response = requests.get(url + "/blob/master/contributors.md")
        response.raise_for_status()

        # Parse the JSON response
        content = response.json()
        show_popup(
            content["payload"]["blob"]["richText"], "INFO", ["OK"], "Contributor(s)")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching contributors: {e}")


def supporters():
    url = os.getenv('GITHUB_URL')

    try:
        response = requests.get(url + "/blob/master/supporters.md")
        response.raise_for_status()

        # Parse the JSON response
        content = response.json()
        show_popup(
            content["payload"]["blob"]["richText"], "INFO", ["OK"], "Supporters")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching supporters: {e}")


def images_background(app):
    """
    Set the background color for the application's views.

    Args:
        - app: The application main window.
    """
    # Prompt the user to select a color
    color = QColorDialog.getColor()

    if color.isValid():
        # Set backgrounds color
        app.zoom_view.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid red;"
        )

        app.main_view.setStyleSheet((
            f"QGraphicsView {{"
            f"background-color: {color.name()};"
            f"border: 1px solid red; }}"
        ))


def history(app, action_type, index, temp=None, move_type=None):
    """
    Update the history of actions performed in the application.

    Args:
        app: The application main window.
        action_type: The type of action performed.
        index: The index or indices associated with the action.
        temp: The temporary data associated with the action.
        move_type: The type of movement action. Defaults to None.
    """
    # Append the new action to the undo list and clear the redo list
    app.undo.append((action_type, index, temp, move_type))
    app.redo.clear()


def numerical_sort(string):
    """Key function for sorting strings with two numbers.

    This function extracts two numerical parts from a string and combines them into a
    single integer. It is intended to be used as the key function in sorting operations
    to achieve sorting based on two numbers.

    Args:
        _string (str): The input string.

    Returns:
        int: The combined numerical value of the two parts, or a default value if no
            numerical parts are found.
    """
    # Extract numerical parts from the string
    matches = re.findall(r'\d+', string)
    if len(matches) >= 2:
        number1 = int(matches[0])
        number2 = int(matches[1])
        # Adjust the multiplier as per your requirements
        combined_number = (number1 * 100) + number2
        return combined_number

    # Return a default value that can be compared
    return sys.maxsize


def get_key_from_value(dictionary, value):
    """
    Retrieve a key in a dictionary from its value.

    Args:
        - dictionary: The dictionary to loop into.
        - value: The value to retrieve the key from
    """
    for key, val in dictionary.items():
        if val == value:
            return key
    return None


def exception_handler(exception_type, exception_value, exception_traceback):
    error = traceback.format_exception(
        exception_type, exception_value, exception_traceback)
    formatted_error = "<br>".join(error)
    show_popup(f"""
        <h2>Uncaught Exception:</h2>
        <h3>You might need to restart the application.</h3>
        <pre>{formatted_error}</pre><br>
        """, "WARNING", ["OK"], "Unexpected Error")


def show_releases_notes(app):
    # Retrieve the image which will be used as an icon for the button
    if getattr(sys, 'frozen', False):
        parent_folder = sys._MEIPASS
    else:
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.abspath(
            os.path.join(current_path, "../.."))

    changelog_path = os.path.join(
        parent_folder, "changelog.md")

    app.release_notes = main_window.MarkdownViewer(
        "Releases Notes", changelog_path)
    app.release_notes.show()
