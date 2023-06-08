#================================================================================#
# File: maths.py
# Created Date: 04-06-2023 | 22:56:53
# Author: Hereiti
#================================================================================
# Last Modified: 08-06-2023 | 11:48:30
# Modified by: Hereiti
#================================================================================
# License: LGPL
# Copyright (c) [2023] [Costantin Hereiti] - All Rights Reserved.
# See the LICENSE file for more information.
#================================================================================#

#================================================================================#
# Built-in imports
#================================================================================#
import re
from typing import Tuple

#================================================================================#
# Local imports
#================================================================================#
from modules.config import config_get
from modules.maps import tileset
#================================================================================#
# Functions
#================================================================================#
def cell_size() -> int:
    """
    Get the cell size based on the configuration.
    
    Returns:
        - The size of each grid cell in pixels.
    """
    if config_get("TYPE") == "Faces":
        return 144

    if config_get("TYPE") == "SV Actor":
        return 64

    _config_size = config_get("CELL SIZE")
    _possibilities = {
        "16x16": 16,
        "24x24": 24,
        "32x32": 32,
        "48x48": 48
    }

    # Return config size or default value.
    if _config_size in _possibilities:
        return _possibilities.get(_config_size)

    match = re.match(r"(\d+)x(\d+)", _config_size)
    if match:
        return int(match.group(1))

    return 32

def index(_x: int, _y: int) -> Tuple[int, int]:
    """
    Get the grid index based on the pixel coordinates.

    Args:
        - x: The x-coordinate in pixels.
        - y: The y-coordinate in pixels.
    
    Returns:
        - The grid index as a tuple (column, row).
    """
    _cell_size = cell_size()
    _x = int(_x // _cell_size)
    _y = int(_y // _cell_size)
    return (_x, _y)

def origin(_index: Tuple[int, int]) -> Tuple[int, int]:
    """
    Get the pixel coordinates of the cell origin for a given index.
    
    Args:
        - The grid index as a tuple (column, row).
    
    Returns:
        - The Coordinates in pixel of a cell origin as a tuple (x, y)
    """
    _cell_size = cell_size()
    _x, _y = _index[0] * _cell_size, _index[1] * _cell_size
    return (_x, _y)

def max_col(app: 'classes.MainWindow.MainWindow') -> int:
    """
    Get the column index of the furthest item.
    
    Args:
        - app: Instance of the MainWindow class.

    Returns:
        - Furthest column index
    """
    if app.images:
        return max(app.images.keys(), key=lambda x: x[0])[0]
    return -1

def max_row(app: 'classes.MainWindow.MainWindow') -> int:
    """
    Get the row index of the lowest item.

    Args:
        - app: Instance of the MainWindow class.

    Returns:
        - Lowest row index
    """ 
    if app.images:
        return max(app.images.keys(), key=lambda x: x[1])[1]
    return -1

def grid_col() -> int:
    """
    Get the number of columns from the configuration.

    Returns:
        - The number of columns in the grid.
    """
    _type = config_get("TYPE")
    if _type == "Tileset":
        _tileset = config_get("TILESET SHEET")
        for key, value in tileset.items():
            if key == _tileset:
                return value["column"]

    if _type == "Faces":
        return 4

    if _type == "SV Actor":
        return 9

    if _type == "Sprites":
        return 12

    return 16

def grid_row() -> int:
    """
    Get the number of rows from the configuration.

    Returns:
        - The number of rows in the grid.
    """
    _type = config_get("TYPE")
    if _type == "Tileset":
        
        _tileset = config_get("TILESET SHEET")
        for key, value in tileset.items():
            if key == _tileset:
                return value["row"]

    if _type == "Faces":
        return 2

    if _type == "SV Actor":
        return 6

    if _type == "Sprites":
        return 8

    return 10000
