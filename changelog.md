# [1.2.0 - ALPHA] - [11/08/2023] #major_update:
#### ADDED:
- ADDED: Update Checker.
- ADDED: Support for multi-selection.
- ADDED: `RGB` support for multi-selection.
- ADDED: `HSV` support for multi-selection.
- ADDED: `Flip` support for multi-selection.
- ADDED: `Rotate` support for multi-selection.
- ADDED: `Resize` support for multi-selection.
- ADDED: `Animation` support for multi-selection.
- ADDED: Dynamic Fetching of supporters and contributors lists.

#### CHANGED:
- CHANGED: Overhaul UI reworked.
- CHANGED: Change buttons panel into a Toolbar.
- CHANGED: Change the editing panel into a Toolbar.
- CHANGED: Preview Image will now be 300x300 instead of 160x160.
- CHANGED: Animation Player will now stop when clicking another cell.
- CHANGED: `Highlight Cell` renamed to `Highlight Cell(s)` and support multi-selection.

#### FIXED:
- FIXED: `Saving All Together` didn't check for lowest row when saving icons sheet.
- FIXED: `Format Folder to MZ` which checked for config cell size instead of calculating from the image size.
- FIXED: `Format Folder to MZ` is now always enable instead of having to select a preset in Holder's Category.
- FIXED: `mouseReleaseEvent` in `graphics_view` which made grid cells bounds calculation unaccurate and prevent the clickable properties. 
___
# [1.1.2 - ALPHA] - [29/06/2023] #minor_update:
#### FIXED:
- FIXED: Typo in `Save All Together` function.
- FIXED: Typo in `Report Issue` function.
___
# [1.1.1 - ALPHA] - [19/06/2023] #minor_update:
#### ADDED:
- ADDED: `Contributors` button in the menu.
- ADDED: `Supporters` button in the menu.
- ADDED: Presets for Balloons and States.
- ADDED: Support for Holder's Content
- ADDED: Custom Grid Option.

#### CHANGED:
- CHANGED: `show_popup` to support RichText.
- CHANGED: Renamed "Type" to "Preset" in the menu.
- CHANGED: Whole code has been rewrote and cleaned.
- CHANGED: Renamed code's modules to better represent what they aim to do.
- CHANGED: Directly changes cell size to fit RPG Maker MZ Presets when selecting presets.

#### FIXED:
- FIXED: `Rotate Slider`'s indicator detection radius has been better optimized.
- FIXED: `Load Folder` wasn't loading in a numerical order.
___
# [1.1.0 - ALPHA] - [04/06/2023] #major_update:
#### Note:
- Editing Update

#### ADDED:
- ADDED: `HSV` editing.
- ADDED: `RGB` editing.
- ADDED: Animation Preview for Characters / SV Actor.
- ADDED: `report bug` button under "help".
- ADDED: Presets for Faces / SV Actors / Sprites.
- ADDED: config file creation date checker.
- ADDED: Clickable edits buttons.
- ADDED: A progress bar for various actions.
- ADDED: Flip Buttons.

#### CHANGED:
- CHANGED: Better Buttons Alignement.
- CHANGED: `View` menu rearranged by adding sub menu.
- CHANGED: Cleaned the code.

#### FIXED:
- FIX: Revert the tentative for a sRBG conversion.
- FIX: Dropped image loaded out of grid bounds.
- FIX: `drag` could duplicate image if clicking to fast.
- FIX: `undo`/`redo` didn't remove the current image before adding the other image.
___
# [1.0.5 - ALPHA] - [04/06/2023] #minor_update:
#### Note:
- QoL Update

#### ADDED:
- ADDED: `save_individually` will now prompt for a file name.
- ADDED: `Drag`/`Drop` of images directly into the grid.
- ADDED: Convert images to sRGB color space.

#### CHANGED:
- CHANGED: `Sheet` renamed to `Add After` which should be more explicit.

#### FIXED:
- FIX: `has_pixel` check for pixels having an alpha higher than 25.
___
# [1.0.4 - ALPHA]- [02/06/2023] #minor_update:
#### Note:
- Initial Public Release

#### FIXED:
- FIX: Graphics View Height out of bounds.
- FIX: Prevent create temp image for empty cells.
- FIX: Prevent saving empty cells in the "save_individually" function.
- FIX: Properly delete index in the move icons event which was causing issue for max_col() and max_row().