import sys
import time
import tkinter as tk
import winreg
import xml.etree.ElementTree as ElTree
from enum import Enum
from math import floor
from shutil import copyfile
from tkinter import filedialog


class Items(Enum):
    Root_vegetables = 15
    Fruits = 706
    Artificial_meat = 707
    Fibers = 1932
    Processed_Food = 179
    Space_food = 712
    Smoke = 77
    Power = 34
    Heat = 73
    CO2 = 64
    Oxygen = 63
    Rubble = 127
    Hazardous_Gas = 971
    Building_tools = 1445
    Energium = 158
    Base_Metals = 157
    Ice = 40
    Noble_Metals = 169
    Carbon = 170
    Raw_Chemicals = 171
    Hyperium = 172
    Energy_block = 1919
    Hull_Block = 1759
    Infrablock = 162
    Soft_block = 1921
    Superblock = 1920
    Techblock = 930
    Bio_Matter = 71
    Chemicals = 176
    Electronics_Component = 173
    Energy_rod = 174
    Fabrics = 177
    Human_meat = 985
    Hyperfuel = 178
    Monster_meat = 984
    Plastics = 175
    Steel_Plates = 1922
    Water = 16
    Optronics_Component = 1924
    Quantronics_Component = 1925
    Energy_Cell = 1926
    Medical_Supplies = 2053
    IV_Fluid = 2058
    Food_group = 1397
    Infra_Scrap = 1873
    Soft_Scrap = 1874
    Hull_Scrap = 1886
    Tech_Scrap = 1946
    Energy_Scrap = 1947
    Credits = 1858


# Look for where steam is installed, only 64-bit is supported.
try:
    hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam")
except:
    hkey = None
    print(sys.exc_info())

try:
    steam_path = winreg.QueryValueEx(hkey, "InstallPath")
except:
    steam_path = None
    print(sys.exc_info())

root = tk.Tk()
root.withdraw()

# Prompt for save file
save_folder = steam_path[0] + '\\steamapps\\common\\SpaceHaven\\savegames\\'
save_file = filedialog.askopenfilename(initialdir=save_folder, title="Select save game file",
                                       filetypes=[("Saved Game", "game")])

# Error out if user selects something other than the save file.
if not save_file.endswith("game"):
    print("Not correct saved game file. Must be named game.")
    sys.exit(0)

# Check if the save file is an XML file that can be read.
try:
    tree = ElTree.parse(save_file)
except:
    print("Not a saved game file")
    sys.exit(0)

game = tree.getroot()

game.findall("./ships/")[0].findall("./characters")[0].findall("./")[0].findall("./pers/attr/")

fill_inv = False
set_attr = False
set_skills = False

while True:
    print("1) Fill Inventory")
    print("2) Set Character's Attributes to 10")
    print("3) Set Character's Skills to 10")
    print("4) All of the above")
    print("0) Quit")
    selection = input("Select")
    if selection == '1':
        fill_inv = True
    if selection == '2':
        set_attr = True
    if selection == '3':
        set_skills = True
    if selection == '4':
        fill_inv = True
        set_attr = True
        set_skills = True
    if selection == '0':
        sys.exit(1)
    break

# List of items that will be skipped
skip_items = [Items.Monster_meat]

storage_number = 0
# Go through the entire save file and edit storage counts
ships = game.findall("./ships/ship")
for ship in ships:
    if ship.find("./settings/[@owner='Player']"):
        print("Ship Name: " + ship.attrib["sname"])
        if set_attr or set_skills:
            for character in ship.findall("./characters/c"):
                if set_attr:
                    print("Setting character points to 10")
                    for attr in character.findall("./pers/attr/"):
                        attr.attrib["points"] = str(10)
                if set_skills:
                    print("Setting character skills to 10")
                    for skills in character.findall("./pers/skills/"):
                        skills.attrib["level"] = skills.attrib["max"]
        if fill_inv:
            for storage in ship.findall("./e/l/feat/inv"):
                if len(storage) > 0:
                    print("Storage:" + str(storage_number))
                    storage_number = storage_number + 1
                    count: int = floor(250 / len(storage))
                    for inventory in storage:
                        try:
                            # Skip Items
                            if Items(int(inventory.attrib['elementaryId'])) in skip_items:
                                print("Skipping " + Items(int(inventory.attrib['elementaryId'])).name)
                                continue
                            print("\t" + Items(int(inventory.attrib['elementaryId'])).name + " " + inventory.attrib[
                                'inStorage'] + " -> " + str(count))
                            inventory.attrib['inStorage'] = str(count)
                        except ValueError:
                            print("Item not in list, ID:" + inventory.attrib['elementaryId'])

# Make a backup, in case something breaks
time = time.strftime("%Y%m%d-%H%M%S")
copyfile(save_file, save_file + "." + time + ".shsge.backup")
# Save changes to selected saved game
tree.write(save_file)
