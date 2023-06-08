#================================================================================#
# File: config.py
# Created Date: 04-06-2023 | 23:28:10
# Author: Hereiti
#================================================================================
# Last Modified: 07-06-2023 | 23:39:10
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
import configparser
import datetime
import logging
import os
import sys

#================================================================================#
# Functions
#================================================================================#
def ensure_config() -> str:
    """
    Ensure that the config file exists and returns the path.
    
    Returns:
        - str: The path to the config file.
    """
    # Get the path to the user's document directory
    _document_dir = os.path.expanduser("~\\OneDrive\\Documents")

    # Create the path to the config directory
    _config_dir = os.path.join(_document_dir, "Hereiti - Set Manager")

    if not os.path.exists(_config_dir):
        # Create the config directory if it doesn't exist
        os.makedirs(_config_dir)

    # Create the path to the config file
    _config_file = os.path.join(_config_dir, "config.ini")

    if os.path.isfile(_config_file):
        # Get the modification timestamp of the file
        _modification_time = os.path.getmtime(_config_file)
        # Specify the comparaison date
        _desired_date = datetime.datetime(2023, 6, 7)

        # Convert the modification timestamp to a datetime object
        _modification_datetime = datetime.datetime.fromtimestamp(_modification_time)

        if _modification_datetime < _desired_date:
            # The file was created before the desired date
            os.remove(_config_file)
        else:
            # Return the path to the existing config file
            return _config_file

    # Create a config file and return its path
    return create_config(_config_file)

def create_config(config_file: str) -> str:
    """
    Create the configuration file with default settings
    
    Args:
        - config_file (str): The path to the configuration file.

    Returns:
        - str: The path to the created configuration file.
    """
    # Create a new configparser object
    _config = configparser.ConfigParser()

    # Add the "General" section to the configparser object
    _config.add_section("General")

    # Set multiple parameter in the "General" section
    _config.set("General", "Type", "Icons")
    _config.set("General", "Cell Size", "32x32")
    _config.set("General", "Tileset Sheet", "A1-A2")
    _config.set("General", "Background-color", "#da69db")
    _config.set("General", "experimental-features", "Enabled")
    _config.set("General", "Creator Compatibility", "None")

    # Write the configparser object to the config file
    with open(config_file, "w", encoding="utf-8") as config_file:
        _config.write(config_file)

    return config_file

def config_get(key: str) -> str:
    """
    Retrieve a configuration value based on a provided key.
    
    Args:
        - key (str): The key corresponding to the desired value.
    
    Returns:
        - str: The configuration value associated to the provided key.
    """
    # Get the path to the config file
    _config_file = ensure_config()

    # Create a new configparser object
    _config = configparser.ConfigParser()

    # Read the config file
    _config.read(_config_file)

    # Retrieve the config value from the "General" section based on the provided key
    value = _config.get("General", key)

    # Return the config value
    return value

def config_set(key: str, value: str) -> None:
    """
    Set a configuration value for the provided key.
    
    Args:
        - key (str): The key corresponding to the configuration value
            to be set.
        - value (str): The new value to be assigned.
    
    Returns:
        - None
    """
    # Get the path to the config file
    _config_file = ensure_config()

    # Create a new configparser object
    _config = configparser.ConfigParser()

    # Read the config file
    _config.read(_config_file)

    # Set the configuration value in the "General" section
    _config.set("General", key, value)

    # Write the updated configuration to the config file
    with open(_config_file, "w", encoding="utf-8") as _config_file:
        _config.write(_config_file)

def exception() -> str:
    """
    Set up exception handling and logging.
    Returns:
        str: the name of the log file created
    """

    # Get the path to the documents directory
    documents_dir = os.path.expanduser("~\\OneDrive\\Documents")

    # Create the exception directory if it doesn't exist
    exception_dir = os.path.join(documents_dir, "Hereiti - Set Manager")
    if not os.path.exists(exception_dir):
        os.makedirs(exception_dir)

    # Create the logs directory if it doesn't exist
    exc_dir = os.path.join(exception_dir, "logs")
    if not os.path.exists(exc_dir):
        os.makedirs(exc_dir)

    # Generate the log file name using the current time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_name = f"error_{current_time}.log"
    error_file = os.path.join(exc_dir, log_name)

    # Configure the logging module to write logs to the file
    logging.basicConfig(
        filename=error_file,
        level=logging.ERROR,
        format='%(asctime)s [%(levelname)s]: %(message)s'
    )

    # Define the exception handler function
    def exception_handler(exc_type, exc_value, exc_traceback):
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Set the custom exception handler for uncaught exceptions
    sys.excepthook = exception_handler

    return log_name
