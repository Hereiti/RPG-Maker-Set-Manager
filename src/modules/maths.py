#!/usr/bin/env python
"""maths.py"""

import re
from modules import config


def cell_size():
    """
    Get the cell size based on the configuration.

    Returns:
        - A tuple representing the rectangle width and height
    """
    # Retrieve size from the config file
    config_size = config.config_get("CELL SIZE")

    # Check that the config size is format as (int)x(int)
    match = re.match(r"(\d+)x(\d+)", config_size)
    if match:
        return (int(match.group(1)), int(match.group(2)))

    return (32, 32)


def grid_col():
    """
    Get the number of columns from the configuration.

    Returns:
        - Number of columns in the grid.
    """
    grid_columns = config.config_get("GRID COLUMNS")

    if grid_columns.isdigit():
        return int(grid_columns)

    return 16


def grid_row():
    """
    Get the number of rows from the configuration.

    Returns:
        - The number of rows in the grid.
    """
    grid_rows = config.config_get("GRID ROWS")

    if grid_rows.isdigit():
        return int(grid_rows)

    return 10000


def cell_index(x, y):
    """
    Get the grid index based on the pixel coordinates.

    Args:
        - x: The x-coordinate in pixels.
        - y: The y-coordinate in pixels.

    Returns:
        - The grid index as a tuple (column, row).
    """
    cell_width, cell_height = cell_size()
    x = int(x // cell_width)
    y = int(y // cell_height)
    return (x, y)


def cell_origin(index):
    """
    Get the pixel coordinates of the cell top left corner.

    Args:
        - The grid index as a tuple (column, row).

    Returns:
        - The coordinates in pixel of the cell top left corner.
    """
    cell_width, cell_height = cell_size()
    x = int(index[0] * cell_width)
    y = int(index[1] * cell_height)
    return (x, y)


def max_col(app):
    """
    Get the column index of the furthest item.

    Args:
        - app: The application main window.

    Returns:
        - Furthest column index.
    """
    if app.images:
        return max(app.images.keys(), key=lambda x: x[0])[0]
    return -1


def max_row(app):
    """
    Get the row index of the lowest item.

    Args:
        - app: The application main window.

    Returns:
        - Lowest row index.
    """
    if app.images:
        return max(app.images.keys(), key=lambda x: x[1])[1]
    return -1
