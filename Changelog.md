# 1.0.4 - Initial Public Release #minor_update:
  ##### Fixes:
  > - Graphics View Height out of bounds.
  > - Prevent create temp image for empty cells.
  > - Prevent saving empty cells in the "save_individually" function.
  > - Properly delete index in the move icons event which was causing issue for max_col() and max_row().

# 1.0.5 - QOL #minor_update:
  #### New Features
  > - Added: Possibility to input the name for files created by "save_individually".
  > - Change: "Sheet" renamed to "Add After" which should be more explicit.
  > - Added: Drag/Drop of images from the explorer.
  
  ##### Fixes:
  > - Check for pixel's alpha higher than 25 instead of any pixel inside of "save_individually".
  > - Change App title & "About" to properly reflect the version.
  > - Convert images to sRGB color space.

# 1.1.0-Alpha - EDITING #major_update:
  #### New Features:
  > - HSV manipulation.
  > - RGB manipulation.
  > - Animation for Characters / SV Actor.
  > - Add a "report bug" button under "help".
  > - Support for Faces / SV Actors / Sprites.
  > - Added a config.ini creation time checker.
  > - Clickable edits buttons on the right menu.
  > - Added a progress bar to actions performed.
  > - Ability to flip horizontally or vertically.

  #### Changes:
  > - Resized the main view to get align with the left buttons.
  > - Rearrange the view menu by adding subcategories.
  > - Did a lot of cleanup of the previous code.
  > - Renamed some configuration parameters.

  #### Fixes:
  > - Revert sRBG conversion
  > - Fixed a bug about drop being loaded out of bounds.
  > - Fixed a bug that prevents the loading of some images (such as default rtp).
  > - Fixed a bug from the "drag" method that could cause an issue if click too quickly at the limit of the cell.
  > - Fixed a bug about undo/redo which didn't properly removed items from the scene before adding back the previous image.
