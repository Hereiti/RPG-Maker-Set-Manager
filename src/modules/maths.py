#================================================================================#
# File: maths.py
# Created Date: 22-05-2023 | 09:27:11
# Author: Hereiti
#================================================================================
# Last Modified: 02-06-2023 | 08:24:04
# Modified by: Hereiti
#================================================================================
# License: LGPL v3
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Standard Library Imports
#================================================================================#
from typing import Tuple

#================================================================================#
# Local Application Imports
#================================================================================#
from modules.config import get_config
from modules        import maps

#================================================================================#
# Functions
#================================================================================#
def cell_size() -> int:
    """
    Get the cell size based on the configuration.

    Returns:
        The size of each cell in pixels.
    """
    config_cell_size = get_config("Cell Size")
    possibilities = {"16x16": 16, "24x24": 24, "32x32": 32, "48x48": 48}
    return possibilities.get(config_cell_size, 32)

def index(_x: int, _y: int) -> Tuple[int, int]:
    """
    Get the grid index based on the pixel coordinates.

    Args:
        x: The x-coordinate in pixels.
        y: The y-coordinate in pixels.

    Returns:
        The grid index as a tuple (column, row).
    """
    _cell_size = cell_size()
    _x = int(_x / _cell_size)
    _y = int(_y / _cell_size)
    return (_x, _y)

def origin(_x: int, _y: int) -> Tuple[int, int]:
    """
    Get the pixel coordinates of the grid origin for a given grid index.

    Args:
        x: The column index.
        y: The row index.

    Returns:
        The pixel coordinates of the grid origin as a tuple (x, y).
    """
    _cell_size = cell_size()
    _x, _y = _x * _cell_size, _y * _cell_size
    return (_x, _y)

def max_col(app: 'classes.MainWindow.MainWindow') -> int:
    """
    Get the maximum column index of the loaded icons.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        The maximum column index.
    """
    if app.icons:
        return int(max(app.icons, key=lambda x: x[0])[0])
    return -1

def max_row(app: 'classes.MainWindow.MainWindow') -> int:
    """
    Get the maximum row index of the loaded icons.

    Args:
        app: The instance of the MainWindow class.

    Returns:
        The maximum row index.
    """
    if app.icons:
        return int(max(app.icons, key=lambda x: x[1])[1])
    return -1

def grid_col() -> int:
    """
    Get the number of columns in the grid.

    Returns:
        The number of columns in the grid.
    """
    _type = get_config("Type")
    _tileset = get_config("Tileset")
    if _type == "Tileset":
        for key, value in maps.tileset.items():
            if key == _tileset:
                return value["column"]
    return 16

def grid_row() -> int:
    """
    Get the number of rows in the grid.

    Returns:
        The number of rows in the grid.
    """
    _type = get_config("Type")
    _tileset = get_config("Tileset")
    if _type == "Tileset":
        for key, value in maps.tileset.items():
            if key == _tileset:
                return value["row"]
    return 10000
