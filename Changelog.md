# 1.0.4 - Initial Public Release:
  ##### Fix(es):
  > - Graphics View Height out of bounds
  > - Prevent saving empty cells in the "save_individually" function
  > - Properly delete index in the move icons event which was causing issue for max_col() and max_row()
  > - Prevent create temp image for empty cells

# 1.0.5 - Small QoL Update:
  > - Added: Drag/Drop of images from the explorer
  > - Added: Possibility to input the name for files created by "save_individually"
  > - Change: "Sheet" renamed to "Add After" which should be more explicit
  
  ##### Fix(es):
  > - Convert images to sRGB color space
  > - Check for pixel's alpha higher than 25 instead of any pixel inside of "save_individually"
  > - Change App title & "About" to properly reflect the version
