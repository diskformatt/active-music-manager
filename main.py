import tkinter as tk
import os, shutil, datetime, configparser

class Interface:

    def __init__(self):
        self.window = tk.Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("Active Music Manager")

        self.cList = []
        self.rList = []

        # delaration of tkinter widgets, then defining them in update()
        self.cView = None
        self.rView = None
        self.moveButton = None
        self.update(True)   # when interface is created, it needs data to draw from right away, so the constructor requires active/archive lists.

    def initList(self, gName: str, gList: list, gColumn: int, gBackground: str):
        # frame to contain listbox and label
        result = tk.Frame(master=self.window, name=(gName.lower()+"Frame"))
        result.grid(row=1, column=gColumn, pady=(0,20))

        # listbox that shows gList
        captions = [f'{item["artist"]} - {item["name"]}' for item in gList] # what shows in the listbox
        s = tk.StringVar()
        s.set(captions)
        box = tk.Listbox(master=result, height=20, width=50, listvariable=s, bg=gBackground, name="list")
        box.grid(row=1)
        for i in range(0,len(gList),2): # zebra striping
            box.itemconfig(i, bg="white")

        # label
        l = tk.Label(master=result, width=50, text=f'{gName} ({len(gList)})')
        l.grid(row=0)

        return result

    def update(self, firstLaunch):
        # updating library lists
        self.cList = indexAlbums(DIR_ACTIVE)
        self.rList = indexAlbums(DIR_ARCHIVE)

        # destroy any existing widgets
        if not firstLaunch:
            self.cView.destroy()
            self.rView.destroy()
            self.moveButton.destroy()

        # GUI is structured as such:
        # "view" vars are frames which contain the list and a label above the list
        # moveButton is placed in between
        self.cView = self.initList("Active", self.cList, 0, "honeydew")
        self.rView = self.initList("Archived", self.rList, 2, "bisque")
        self.moveButton = tk.Button(master=self.window, text="\n  Move  \n", command=self.requestMove)
        self.moveButton.grid(row=1, column=1)

    # get the selected album from the gui, and pass it to function to move album
    # detects what list selection is in with focus_get()
    def requestMove(self):
        self.moveButton["state"] = "disabled" # disable move button while move is being performed
        try:
            index = self.window.focus_get().curselection()[0]
            if self.window.focus_get().master == self.cView:    moveAlbum(self.cList[index], DIR_ARCHIVE)
            elif self.window.focus_get().master == self.rView:  moveAlbum(self.rList[index], DIR_ACTIVE)
            else:
                print("selection could not be parsed.")
        except Exception as e:
            print("There was an error in Interface.requestMove:", e)
        
        # refresh the gui by destroying existing widgets and re-creating them
        self.update(False)

        return

# use the folder structure of active and archived music directories to create a list representing current status of music library
def indexAlbums(gDir):
    if len(os.listdir(gDir)) == 0: return [] # if folder to check is empty
    results = []
    for root, dirs, _ in os.walk(gDir):
        # "if not dirs" will only return lowest-level folders (expects albums in artist folders)
        if not dirs: results.append({
            "path": root,
            # "isActive": True,
            "name": os.path.basename(root),
            "artist": os.path.basename(os.path.dirname(root))
        }) 
    return results

# attempt to move an album folder between active and archive directories.
# albumDict is a dictionary containing full album path and information for creating destination folder.
# dstRoot is the root folder of the destination, above artist and album name folders. (expected path structure: root -> artist -> album)
def moveAlbum(albumDict, dstRoot):
    # define destination folder
    dstArtist = os.path.join(
        dstRoot,
        albumDict["artist"]
    )

    # attempt folder move
    try:
        os.makedirs(dstArtist, exist_ok=True) # makes album subfolder
        shutil.move(albumDict["path"], dstArtist)
        print("Moved sucessfully.")
    except Exception as e:
        print("Failed to move:", e)
        return False
    
    # if artist folder in source is empty, delete it
    oldArtistFolder = os.path.dirname(albumDict["path"])
    if len(os.listdir(oldArtistFolder)) == 0:
        try:
            os.rmdir(oldArtistFolder)
            print("Empty directory", oldArtistFolder, "deleted")
        except Exception as e:
            print(oldArtistFolder, "is empty, but could not be deleted:", e)
        
    # log change in file
    with open(LOGNAME, 'a', encoding="utf-8") as f:
        f.write(
            ("Archived" if dstRoot == DIR_ARCHIVE else "Activated") +
            f'\t{albumDict["artist"]} - {albumDict["name"]}\n'
        )

    return True

# get constants from conf file and start new section in log file
config = configparser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'setup.conf'))
DIR_ACTIVE = os.path.realpath(config['paths']['active'])
DIR_ARCHIVE = os.path.realpath(config['paths']['archive'])
LOGNAME = os.path.realpath(os.path.join(os.path.dirname(__file__), config['paths']['logname']))
with open(LOGNAME, 'a') as f: f.write(f'\nNew session: {str(datetime.datetime.now().strftime('%Y-%m-%d @ %H:%M'))}\n')

gui = Interface()
gui.window.mainloop()