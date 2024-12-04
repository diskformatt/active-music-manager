# Active Music Manager
I wrote this program to allow me to quickly swap music albums between an "active" folder and "archive" folder on my computer. Albums that are "active" are those I intend to have downloaded to my phone. Despite this, I decided that programatically making the changes on the phone would be beyond the current scope of this project:
- iPhone internal storage is completely inacessile on computer unless syncing through iTunes.
- Android uses MTP to transfer files, which is difficult to leverage on Windows without using File Explorer.

Therefore the program simply performs the changes to the local directories, and logs them to a text file for the user to perform on the phone themselves. 

Alongside creating a useful tool, I also used this project to explore these Python concepts:
- ternary operations
- list enumeration
- "anonymous" variables (as opposed to declaring a variable, just to use it only once immediately after)
- defining constants through a config file
- Dictionary creation and lookup
- os, shutil, and tkinter libraries
- exception handling

Although all libraries used should be cross-platform, this program has only been tested on Windows 11 with Windows-style folder paths.

### Folder Structure
The folder structure expected by this program is `root -> artist name -> album name` for both active and archived music.
The root directories for active and archived music are defined in `./setup.conf`. This file must be in the same folder as the program.

If an artist directory is left empty after a move, it is automatically deleted.