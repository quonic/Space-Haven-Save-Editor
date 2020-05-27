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

ship_counter = 0
ship_number = 0
ship_list = []

# Prompt for selection of ship
# todo detect player owned ships
print("Ship Names")

for i in game.getchildren():
    if i.tag == 'ships':
        for j in i.getchildren():
            print(str(ship_counter) + ") " + j.attrib['sname'])
            ship_list.append(j.attrib['sname'])
            ship_counter = ship_counter + 1
while True:
    ship_number = input("Enter the number of your ship")
    if int(ship_number) < ship_counter:
        break

storage_number = 0
# Go through the entire save file and edit storage counts
for i in game.getchildren():
    if i.tag == 'ships':
        for j in i.getchildren():
            # Only edit the selected ship
            if j.attrib['sname'] == ship_list[int(ship_number)]:
                print(j.attrib['sname'])
                for k in j.getchildren():
                    if len(k) > 0:
                        for l in k.getchildren():
                            if l.tag == 'l':
                                for m in l.getchildren():
                                    if m.tag == 'feat':
                                        for n in m.getchildren():
                                            if n.tag == 'inv' and len(n.getchildren()) > 0:
                                                print("Storage:" + str(storage_number))
                                                storage_number = storage_number + 1
                                                count: int = floor(250 / len(n.getchildren()))
                                                for inventory in n.getchildren():
                                                    try:
                                                        if Items(int(inventory.attrib[
                                                                         'elementaryId'])) == Items.Monster_meat:
                                                            print("Skipping Monster Meat")
                                                            continue
                                                        print("\t" + Items(int(
                                                            inventory.attrib['elementaryId'])).name + " " +
                                                              inventory.attrib['inStorage'] + " -> " + str(
                                                            count))
                                                        inventory.attrib['inStorage'] = str(count)
                                                    except ValueError:
                                                        print(
                                                            "Item not in list, ID:" + inventory.attrib['elementaryId'])

# Make a backup, in case something breaks
time = time.strftime("%Y%m%d-%H%M%S")
copyfile(save_file, save_file + "." + time + ".shsge.backup")
# Save changes to selected saved game
tree.write(save_file)
