#================================================================================#
# File: config.py
# Created Date: 22-05-2023 | 08:12:38
# Author: Hereiti
#================================================================================
# Last Modified: 30-05-2023 | 08:25:56
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Import
#================================================================================#
import configparser
import datetime
import logging
import os
import sys

#================================================================================#
# Functions
#================================================================================#
def check_config() -> str:
    """
    Checks the configuration and returns the path to the config file.
    Returns:
        str: The path to the config file.
    """
    # Get the path to the user's documents directory
    documents_dir = os.path.expanduser("~\\OneDrive\\Documents")

    # Create the path to the config directory
    config_dir = os.path.join(documents_dir, "Hereiti - Set Manager")

    if not os.path.exists(config_dir):
        # Create the config directory if it doesn't exist
        os.makedirs(config_dir)
        print(f"Config directory '{config_dir}' created.")

    config_file = os.path.join(config_dir, "config.ini")
    # Create the path to the config file

    if os.path.isfile(config_file):
        # Return the path to the existing config file
        return config_file

    # Create the config file and return its path
    return create_config(config_file)

def create_config(config_file: str) -> str:
    """
    Create a configuration file with default settings.
    Args:
        config_file (str): The path to the configuration file.
    Returns:
        str: The path to the created configuration file.
    """
    # Create a new configparser object
    config = configparser.ConfigParser()

    # Add the "General" section to the configparser object
    config.add_section("General")

    # Set the "Type" parameter in the "General" section
    config.set("General", "Type", "Icon Set")
    # Set the "Cell Size" parameter in the "General" section
    config.set("General", "Cell Size", "32x32")
    # Set the "Tileset" parameter in the "General" section
    config.set("General", "Tileset", "A1-A2")
    # Set the "Background-color" parameter in the "General" section
    config.set("General", "Background-color", "#da69db")

    # Write the configparser object to the config file
    with open(config_file, "w", encoding="utf-8") as configfile:
        config.write(configfile)

    # Print a message indicating the creation of the config file
    print(f"Config file '{config_file}' created in the config directory")

    # Return the path to the created config file
    return config_file

def get_config(key: str) -> str:
    """
    Retrieve a configuration value based on the provided key.
    Args:
        key (str): The key corresponding to the desired configuration value.
    Returns:
        str: The configuration value associated with the provided key.
    """
    # Get the path to the config file
    config_file = check_config()

    # Create a new configparser object
    config = configparser.ConfigParser()

    # Read the config file
    config.read(config_file)

    # Retrieve the configuration value from the "General" section based on the provided key
    value = config.get("General", key)

    # Return the configuration value
    return value

def set_config(key: str, value: str) -> None:
    """
    Set a configuration value for the provided key.
    Args:
        key (str): The key corresponding to the configuration value to be set.
        value (str): The new value to be assigned to the configuration key.
    Returns:
        None
    """
    # Get the path to the config file
    config_file = check_config()

    # Create a new configparser object
    config = configparser.ConfigParser()

    # Read the config file
    config.read(config_file)

    # Set the configuration value in the "General" section
    config.set("General", key, value)

    # Write the updated configuration to the config file
    with open(config_file, "w", encoding="utf-8") as configfile:
        config.write(configfile)

    # Print a message confirming the change in the config file
    print(f"Config key '{key}' changed to '{value}' in the config file.")

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
