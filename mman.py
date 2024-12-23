import os, shutil, datetime, configparser, colorama

# get global constants from conf file and start new section in log file
try:
    config = configparser.RawConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'settings.conf'))
    DIR_ACTIVE = os.path.realpath(config['paths']['active'])
    DIR_ARCHIVE = os.path.realpath(config['paths']['archive'])
    LOGNAME = os.path.realpath(os.path.join(os.path.dirname(__file__), config['paths']['logname']))
    with open(LOGNAME, 'a') as f: f.write(f'\nNew session: {str(datetime.datetime.now().strftime('%Y-%m-%d @ %H:%M'))}\n')
except Exception as e: print(e); quit()
colorama.init()

# returns list of albums in both folders sorted by artist name. Each album is a dictionary.
def initAlbumList():

    # returns list of lowest-level subfolders.
    def scan(folder: str, activeStatus: bool):
        
        # assert folder exists
        if not os.path.exists(folder): raise Exception("Could not find either your active or archive folder. Check their definitions in settings.conf")

        # create list of subfolders
        out = []
        for root, dirs, _ in os.walk(folder):
            if not dirs:
                out.append({
                    "name": os.path.basename(root), 
                    "artist": os.path.basename(os.path.dirname(root)), 
                    "active": activeStatus})

        # handle edge case where active or archvied folder is empty: clear respective list and print warning
        if (out[0]["name"] == os.path.basename(folder)) and (out[0]["artist"] == os.path.basename(os.path.dirname(folder))):
            out = []
            print("One of your library folders was detected as empty.")

        return out

    # use scan() to compile subfolder lists for active and archived folders.
    try:
        active = scan(DIR_ACTIVE, True)
        archived = scan(DIR_ARCHIVE, False)
    except Exception as e: raise Exception(f"Could not complete music folders scan: {e}")

    # check for albums which are both active and archived.
    cNames = [f"{i["artist"]} - {i["name"]}" for i in active]
    rNames = [f"{i["artist"]} - {i["name"]}" for i in archived]
    common = list(set(cNames).intersection(rNames))
    if common: raise Exception(f"The following albums are both active and archived:\n{common}\nHandle these discrepencies before continuing.")

    return sorted((active + archived), key=lambda d: d["artist"].lower()) # .lower() ensures case insensitive sorting

# lists albums from "albums" (defined by initAlbumList when program starts).
def listAlbums(albums: list, cat: str):

    # validate cat
    if not cat in ["all", "active", "archived"]: raise Exception('specify "all", "active", or "archived"')
    
    cCount = 0
    rCount = 0
    print("")
    for i, item in enumerate(albums):
        if item["active"]: 
            cCount += 1
            if cat in ["all", "active"]: print(f"{colorama.Back.GREEN}{i:03d}. {item["artist"]} - {item["name"]}{colorama.Style.RESET_ALL}")
        else:
            rCount += 1
            if cat in ["all", "archived"]: print(f"{colorama.Back.RED}{i:03d}. {item["artist"]} - {item["name"]}{colorama.Style.RESET_ALL}")
    
    # print totals
    print(f"\n{cCount} active; {rCount} archived\n")
    
    return

# move an album given its information from master album list. Entry in master list is determined in the input loop.
def moveAlbum(album: dict):

    # define variables based on whether or not album is currently active or archived
    try:
        if album["active"]:
            src = os.path.join(DIR_ACTIVE, album["artist"], album["name"])
            dst = os.path.join(DIR_ARCHIVE, album["artist"], album["name"])
            action = "archive"
        else:
            src = os.path.join(DIR_ARCHIVE, album["artist"], album["name"])
            dst = os.path.join(DIR_ACTIVE, album["artist"], album["name"])
            action = "activate"
    except Exception as e: raise Exception(f"Could not deduce destination path: {e}")
    
    # attempt to move folder
    print(f"Attepting to {action} {album["artist"]} - {album["name"]}")
    try: shutil.move(src, dst)
    except Exception as e: raise Exception(f"Error during move: {e}")
    print("done")

    # delete artist folder if it is now empty
    srcArtist = os.path.dirname(src)
    if len(os.listdir(srcArtist)) == 0:
        try: os.rmdir(srcArtist)
        except Exception as e: raise Exception(f"{srcArtist} is empty, but could not be deleted: {e}")

    return f"{action}d {album["artist"]} - {album["name"]}"

def main():
    print("Indexing album folders...")
    try: allAlbums = initAlbumList()
    except Exception as e: print(e); quit()
    listAlbums(allAlbums, "all")
    log = []

    while True:
        parts = input().split()

        # catch if nothing is typed
        try: parts[0]
        except: continue

        match parts[0]:
            case "quit" | "q":
                if log: # if moves were made (log list is not empty)
                    print("\nSummary of changes:")
                    for i in log: print(i)
                print("")
                break

            case "list" | "l":
                try: listAlbums(allAlbums, parts[1])
                except Exception as e: print(e); continue

            case "move" | "m":
                try: 
                    target = int(parts[1])
                    if target < 0 or target > 999: raise Exception("accepted values between 0 and 999")
                    action = moveAlbum(allAlbums[target]) # if successful, moveAlbum returns string describing action performed
                except Exception as e: print(e); continue
                
                allAlbums[target]["active"] = not allAlbums[target]["active"] # flip active/album flag in internal album list
                
                # log changes
                log.append(action) 
                with open(LOGNAME, 'a', encoding="utf-8") as f: f.write(f"{action}\n")

            case "hist" | "h":
                if not log: print("No actions have been performed yet.")
                else: 
                    for i in log: print(i)

            case "help":
                print("\t(h)ist: show all moves made during the current session.")
                print("\t(l)ist <all, active, archived>: print numbered list of albums.")
                print("\t(m)ove <int>: swap album with index <int> between active and archive folders.")
                print("\t(q)uit: exit the program.")
                print(f"\n\tIn list: {colorama.Back.GREEN}Active albums{colorama.Back.RESET} {colorama.Back.RED}Archived albums{colorama.Back.RESET}\n")

            case _:
                print('Invalid command. Type "help" for list of commands.')
    return
main()