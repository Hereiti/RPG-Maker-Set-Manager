#!/usr/bin/env python
"""config.py"""
import configparser
import datetime
import os


def ensure_config() -> str:
    """
    Ensure that the config file exists and returns the path.

    Returns:
        - str: The path to the config file.
    """
    # Get the path to the config directory
    document_dir = os.path.join(os.path.expanduser("~"), "Documents")
    config_dir = os.path.join(document_dir, "Hereiti - Set Manager")

    if not os.path.exists(config_dir):
        # Create the config directory if it doesn't exist
        os.makedirs(config_dir)

    # Create the path to the config file
    config_file = os.path.join(config_dir, "config.ini")

    if os.path.exists(config_file):
        # Get the modification timestamp of the file
        modification_time = os.path.getmtime(config_file)
        modification_date = datetime.datetime.fromtimestamp(modification_time)
        # Specify the comparaison date
        comparaison_date = datetime.datetime(2023, 7, 31)

        if modification_date < comparaison_date:
            # Remove the file if created before the desired date
            os.remove(config_file)
        else:
            # Return the path to the existing config file
            return config_file

    # Create a config file and return its path
    return create_config(config_file)


def create_config(config_file: str) -> str:
    """
    Create the configuration file with default settings

    Args:
        - config_file (str): The path to the configuration file.

    Returns:
        - str: The path to the created configuration file.
    """
    # Create a new configparser object
    config = configparser.ConfigParser()

    # Add the "General" section to the configparser object
    config.add_section("GENERAL")

    default_config = [
        ("TYPE", "Icons"), ("CELL SIZE", "32x32"), ("TILESET SHEET", "A1-A2"),
        ("BACKGROUND-COLOR", "#da69db"), ("EXPERIMENTAL-FEATURES", "Enabled"),
        ("GRID ROWS", "10000"), ("GRID COLUMNS", "16"), ("CREATOR", "None")
    ]

    for setting in default_config:
        config.set("GENERAL", setting[0], setting[1])

    # Write the configparser object to the config file
    with open(config_file, "w", encoding="utf-8") as config_file:
        config.write(config_file)

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
    config_file = ensure_config()

    # Create a new configparser object
    config = configparser.ConfigParser()

    # Read the config file
    config.read(config_file)

    # Retrieve the config value based on the provided key
    value = config.get("GENERAL", key)

    return value


def config_set(key: str, value: str) -> None:
    """
    Set a configuration value for the provided key.

    Args:
        - key (str): The key corresponding to the configuration value
            to be set.
        - value (str): The new value to be assigned
    """
    # Get the path to the config file
    config_file = ensure_config()

    # Create a new configparser object
    config = configparser.ConfigParser()

    # Read the config file
    config.read(config_file)

    # Set the configuration value in the "GENERAL" section
    config.set("GENERAL", key, value)

    # Write the updated configuration to the config file
    with open(config_file, "w", encoding="utf-8") as config_file:
        config.write(config_file)
