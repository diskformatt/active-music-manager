# Active Music Manager
This program allows me to quickly swap music albums between an "active" folder and "archive" folder on my computer. Albums that are "active" are those I intend to have downloaded to my phone. Despite this, I decided that programatically making the changes on the phone would be beyond the current scope of this project:
- iPhone internal storage is completely inacessile on computer unless syncing through iTunes.
- Android uses MTP to transfer files, which is difficult to leverage on Windows without using File Explorer.

Therefore the program simply performs the changes to the local directories, and logs them to a text file for the user to perform on the phone themselves. 

Alongside creating a useful tool, I also used this project to explore these Python concepts:
- ternary operations
- list enumeration
- "anonymous" variables (as opposed to declaring a variable, just to use it only once immediately after)
- loading user settings from a config file
- Dictionary creation and lookup
- os, shutil, and other libraries (see "Methods Explored")
- exception handling

## Usage
### Requirements
Python is needed with the [colorama library](https://pypi.org/project/colorama/) installed. Although this program should work cross-platform, it has only been tested on Windows 11 with Windows-style folder paths.

### Interface
Upon startup, the program scans the active and archive folders specified in `./settings.conf` and compiles a list of all albums. It assumes both folders follow the structure `root -> artist name -> album name`, recording lowest-level folders as albums.

If successful, the program lists all albums then prompts for input, where the user can input a number of commands:
- `list <all, active, archived>`: Lists albums based on given criteria. Albums in green are active; those in red are archived.
- `move <index>`: Moves an album between active and archived directories based on its numerical `<index>` in the internal list. If an artist directory is left empty after a move, it is automatically deleted.
- `hist`: Show summary of all moves performed in the current session. These are also written to a log file during runtime; by default this file is `mman.log`.
- `quit`: Exit the program, showing summary of all moves before doing so.

## Methods Explored
Throughout development I explored multiple approaches to solving this problem:
- **Terminal-based GUI:** Using the [blessed library](https://blessed.readthedocs.io/en/latest/) to create a Vim-like interface with a header, scrolling content in the middle, and an area at the bottom to type commands.
- **Traditional GUI:** Using [tkinter](https://docs.python.org/3/library/tkinter.html) to create an interface where albums are visually swapped between two lists.
- **SQL Database:** Using Python's built-in [sqllite3 library](https://docs.python.org/3/library/sqlite3.html) to maintain an SQL database of all albums. I intended for the database to also contain additional information about each album that I'm currently keeping in a spreadsheet.

Ultimately, I found these methods added too much needless complexity to a program meant for a relatively simple task. In the spirit of keeping the code easy to maintain, the current version uses none of the above libraries, although it does use colorama to make the list of all albums easier to visually skim through.