# Dark Violet Editor - A Delta Skin mapping editor tool.
# Copyright Dark Violet - All Rights Reserved

from pathlib import Path
from tkinter import *
from tkinter import ttk
import json
import easygui
from pdf2image import convert_from_path
import tempfile

def chooseSize():
    size = input("Choose the screen size you want to change\n1- standard\n2- edgeToEdge\n")

    if size == "1":
        return "standard"
    elif size == "2":
        return "edgeToEdge"
    else:
        print("Selection failed!")
        chooseSize()

def chooseOrientation():
    size = input("Choose the screen size you want to change\n1- landscape\n2- portrait\n")

    if size == "1":
        return "landscape"
    elif size == "2":
        return "portrait"
    else:
        print("Selection failed!")
        chooseOrientation()

def printSkinInfo(skin_info: dict):
    print("Name: {}\nConsole: {}\nSkin Identifier: {}".format(skin_info["name"], skin_info["gameTypeIdentifier"].split(".")[-1], skin_info["identifier"]))

class EditorInterface(Frame):

    def __init__(self, window: Tk = None):
        self.window = window
        self.window.title("Dark Violet Editor")
        self.window.resizable(False, False)

        # Create canvas object to display images
        self.canvas = Canvas(window, width=positions["representations"]["iphone"][size][orientation]["mappingSize"]["width"], height=positions["representations"]["iphone"][size][orientation]["mappingSize"]["height"])

        # Finds image from file and add to interface
        if "resizable" in positions["representations"]["iphone"][size][orientation]["assets"].keys(): # should only be pdf images
            # Use a temp dir to convert pdf to png
            with tempfile.TemporaryDirectory() as tmpdir:
                pages = convert_from_path(str(skinpath) + "/" + positions["representations"]["iphone"][size][orientation]["assets"]["resizable"], size=(positions["representations"]["iphone"][size][orientation]["mappingSize"]["width"], positions["representations"]["iphone"][size][orientation]["mappingSize"]["height"]))
                pages[0].save(tmpdir + "/temp.png", "PNG")

                # Add image to interface from temp dir
                self.image = PhotoImage(file=tmpdir + "/temp.png")
                self.canvas.background = self.canvas.create_image(0, 0, image=self.image, anchor=NW)

        else:
            self.image = PhotoImage(file=str(skinpath) + "/" + positions["representations"]["iphone"][size][orientation]["assets"]["large"])
            self.canvas.background = self.canvas.create_image(0, 0, image=self.image, anchor=NW)

        self.canvas.pack()

        self.scrapButtonsPos(positions)

        self.canvas.elementsE = {}
        self.canvas.elements = {}
        self.canvas.elementsT = {}

        for elem in self.dico:
            self.makeElement(elem)

        self.makeScreens()

    def move(self, press):
        ver = 0
        hor = 0
        if press.keysym == "Right":
            hor += 1
        if press.keysym == "Left":
            hor += -1
        if press.keysym == "Down":
            ver += 1
        if press.keysym == "Up":
            ver += -1

        if hasattr(self, "selectedItem"):
            self.canvas.move(self.canvas.elements[self.selectedItem], hor, ver)
            self.canvas.move(self.canvas.elementsT[self.selectedItem], hor, ver)
            if self.selectedItem in self.canvas.elementsE.keys():
                self.canvas.move(self.canvas.elementsE[self.selectedItem], hor, ver)

            self.dico[self.selectedItem]["frame"]["x"] += hor
            self.dico[self.selectedItem]["frame"]["y"] += ver

    def scrapButtonsPos(self, json):
        self.dico = {}

        for elem in positions["representations"]["iphone"][size][orientation]["items"]:
            if len(elem["inputs"]) > 1:
                self.dico[str(elem["inputs"])] = elem
            else:
                self.dico[elem["inputs"][0]] = elem

    def collision(self, position):
        for key, item in self.dico.items():
            if item["frame"]["x"] < position.x and item["frame"]["x"] + item["frame"]["width"] > position.x:
                if item["frame"]["y"] < position.y and item["frame"]["y"] + item["frame"]["height"] > position.y:
                    self.selectedItem = key


    def makeElement(self, element):

        extend = {}
        if self.dico[element].get("extendedEdges") == None:
            for side in positions["representations"]["iphone"][size][orientation]["extendedEdges"]:
                extend[side] = positions["representations"]["iphone"][size][orientation]["extendedEdges"][side]

        else:
            for side in positions["representations"]["iphone"][size][orientation]["extendedEdges"]:
                if self.dico[element]["extendedEdges"].get(side) == None:
                    extend[side] = positions["representations"]["iphone"][size][orientation]["extendedEdges"][side]
                else:
                    extend[side] = self.dico[element]["extendedEdges"].get(side)

        self.canvas.elementsE[element] = self.canvas.create_rectangle(
        self.dico[element]["frame"]["x"] - extend["left"], #x
        self.dico[element]["frame"]["y"] - extend["top"], #y
        self.dico[element]["frame"]["x"] + self.dico[element]["frame"]["width"] + extend["right"], #width
        self.dico[element]["frame"]["y"] + self.dico[element]["frame"]["height"] + extend["bottom"], #height
        fill = "blue", stipple="gray50")


        self.canvas.elements[element] = self.canvas.create_rectangle(self.dico[element]["frame"]["x"], self.dico[element]["frame"]["y"], self.dico[element]["frame"]["x"] + self.dico[element]["frame"]["width"], self.dico[element]["frame"]["y"] + self.dico[element]["frame"]["height"], fill = "red", stipple="gray50") #posX posY width height
        self.canvas.elementsT[element] = self.canvas.create_text(self.dico[element]["frame"]["x"] + int(self.dico[element]["frame"]["width"]/2), self.dico[element]["frame"]["y"] + int(self.dico[element]["frame"]["height"]/2), text=element)

    def makeScreens(self):
        if "screens" in positions["representations"]["iphone"][size][orientation].keys():
            for i, elem in enumerate(positions["representations"]["iphone"][size][orientation]["screens"]):

                screenName = "screen_" + str(i)

                self.dico[screenName] = {}
                self.dico[screenName]["frame"] = elem["outputFrame"]

                self.canvas.elements[screenName] = self.canvas.create_rectangle(self.dico[screenName]["frame"]["x"], self.dico[screenName]["frame"]["y"], self.dico[screenName]["frame"]["x"] + self.dico[screenName]["frame"]["width"], self.dico[screenName]["frame"]["y"] + self.dico[screenName]["frame"]["height"], fill = "yellow", stipple="gray50")
                self.canvas.elementsT[screenName] = self.canvas.create_text(self.dico[screenName]["frame"]["x"] + int(self.dico[screenName]["frame"]["width"]/2), self.dico[screenName]["frame"]["y"] + int(self.dico[screenName]["frame"]["height"]/2), text=screenName)
                # self.canvas.elementsE[screenName] = self.canvas.create_rectangle(0,0,0,0) #just to avoid errors when moving
        else:
            print("No screens present, using default position.")


    def save(self, osef):

        for elem in self.dico:
            if "screen_" in elem:
                positions["representations"]["iphone"][size][orientation]["screens"][int(elem.split("_")[-1]) - 1]["outputFrame"] = self.dico[elem]["frame"]
            else:
                for i, truc in enumerate(positions["representations"]["iphone"][size][orientation]["items"]):
                    positions["representations"]["iphone"][size][orientation]["items"][i]["inputs"]

        with open(filepath, "w") as file:
            json.dump(file, positions, indent=2)
        print("Changes saved.")

skinpath = Path(easygui.diropenbox(title="Select Skin Folder"))

with open(str(skinpath) + "/info.json", "r") as file:
    positions = json.load(file)

size = chooseSize()
orientation = chooseOrientation()

printSkinInfo(positions)

window = Tk()
gui = EditorInterface(window=window)

window.bind("<Button-1>", gui.collision)

window.bind("<Left>", gui.move)
window.bind("<Right>", gui.move)

window.bind("<Up>", gui.move)
window.bind("<Down>", gui.move)

window.bind("<Control-s>", gui.save)

# window.bind("<MouseWheel>", gui.wheel)

mainloop()
