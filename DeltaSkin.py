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

        self.setupPopup()
        
        self.moveSelect = "globalW"
        
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
                    return key #used now


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
                # self.canvas.elementsE[screenName] = self.canvas.create_rectangle(0,0,0,0) #just to avoid errors when moving lol nice coding
        else:
            print("No screens present, using default position.")


    def save(self, osef):
        
        self.fixScreen = []
        for elem in self.dico:
            if "screen_" in elem:
                self.fixScreen.append(self.dico[elem])
            else:
                for i, truc in enumerate(positions["representations"]["iphone"][size][orientation]["items"]):
                    positions["representations"]["iphone"][size][orientation]["items"][i]["inputs"]
        
        
        #fix a bug where screens were saved the wrong way
        for key, elem in enumerate(reversed(self.dicoFix)):
            positions["representations"]["iphone"][size][orientation]["screens"][key]["outputFrame"] = self.fixScreen[key]["frame"]
        
        with open(str(skinpath) + "/info.json", "w") as file:
            json.dump(positions, file, indent=2)
        print("Changes saved.")
    
    def setupPopup(self):
        self.menu = Menu(window, tearoff = 0) 
        self.menu.add_command(label ="Change left extend", command=lambda: self.setMove("left"))
        self.menu.add_command(label ="Change right extend", command=lambda: self.setMove("right")) 
        self.menu.add_command(label ="Change top extend", command=lambda: self.setMove("top")) 
        self.menu.add_command(label ="Change bottom extend", command=lambda: self.setMove("bottom")) 
        self.menu.add_separator() 
        self.menu.add_command(label ="Remove left extend", command=lambda: self.removeExtend("left"))
        self.menu.add_command(label ="Remove right extend", command=lambda: self.removeExtend("right")) 
        self.menu.add_command(label ="Remove top extend", command=lambda: self.removeExtend("top")) 
        self.menu.add_command(label ="Remove bottom extend", command=lambda: self.removeExtend("bottom")) 
        self.menu.add_separator() 
        self.menu.add_command(label ="Change main width size", command=lambda: self.setMove("globalW")) 
        self.menu.add_command(label ="Change main height size", command=lambda: self.setMove("globalH")) 
        
    def setMove(self, direction):
        self.moveSelect = direction
        
    def popup(self, event):
        if self.collision(event) == None:
            return
        self.collision(event)
        self.menu.tk_popup(event.x_root, event.y_root)
    
    
    def removeExtend(self, element):
        try:
            type(self.selectedItem)
        except AttributeError:
            print('Nothing selected')
            return
        
        try:
            del(self.dico[self.selectedItem]["extendedEdges"][element])
                    
            sides = ["top", "bottom", "left", "right"]
            extend = {}
                    
            for side in sides:
                if self.dico[self.selectedItem]["extendedEdges"].get(side) is None:
                    extend[side] = positions["representations"]["iphone"][size][orientation]["extendedEdges"].get(side)
                else:
                    extend[side] = self.dico[self.selectedItem]["extendedEdges"].get(side)
                    
            self.canvas.coords(self.canvas.elementsE[self.selectedItem],
            self.dico[self.selectedItem]["frame"]["x"] - extend["left"],
            self.dico[self.selectedItem]["frame"]["y"] - extend["top"], 
            self.dico[self.selectedItem]["frame"]["x"] + self.dico[self.selectedItem]["frame"]["width"] + extend["right"],
            self.dico[self.selectedItem]["frame"]["y"] + self.dico[self.selectedItem]["frame"]["height"] + extend["bottom"])

        except KeyError:
            print("Failed to delete the {} extended edge (doesn't exist)".format(element))
    
    
    
    def changeSize(self, event):
        try:
            type(self.selectedItem)
        except AttributeError:
            print('Nothing selected')
            return
                
        
        if event.keysym == "plus":
            n = 1
        else:
            n = -1
        
        if "global" in self.moveSelect:
            x0, y0, width, height = self.canvas.coords(self.canvas.elements[self.selectedItem])
            if not "screen" in self.selectedItem:
                x1, y1, width1, height1 = self.canvas.coords(self.canvas.elementsE[self.selectedItem])
            h=0
            w=0
            if self.moveSelect == "globalW":
                if self.dico[self.selectedItem]["frame"]["width"] + n == 1:
                    print("Can't make an element smaller than 1px (nice try)")
                else:
                    w=n
            
            elif self.moveSelect == "globalH":
                if self.dico[self.selectedItem]["frame"]["height"] + n == 1:
                    print("Can't make an element smaller than 1px (nice try)")
                else:
                    h=n
                    
            self.dico[self.selectedItem]["frame"]["width"] += w
            self.dico[self.selectedItem]["frame"]["height"] += h
            self.canvas.coords(self.canvas.elements[self.selectedItem], x0, y0, width+w, height+h)
            self.canvas.coords(self.canvas.elementsT[self.selectedItem], x0 + int(self.dico[self.selectedItem]["frame"]["width"]/2), y0+ int(self.dico[self.selectedItem]["frame"]["height"]/2))
            if not "screen" in self.selectedItem:
                self.canvas.coords(self.canvas.elementsE[self.selectedItem], x1, y1, width1+w, height1+h)
        
        elif "screen" in self.selectedItem:
            print("You can't change the extend of screens")
        
        else:
                
            if self.dico[self.selectedItem]["extendedEdges"].get(self.moveSelect) is None :
                self.dico[self.selectedItem]["extendedEdges"][self.moveSelect] = 0
            if self.dico[self.selectedItem]["extendedEdges"][self.moveSelect] + n < 0:
                print("extended edges can't be negative")
                return
            else:
                self.dico[self.selectedItem]["extendedEdges"][self.moveSelect] += n
                
            sides = ["top", "bottom", "left", "right"]
            extend = {}
                    
            for side in sides:
                if self.dico[self.selectedItem]["extendedEdges"].get(side) is None:
                    extend[side] = positions["representations"]["iphone"][size][orientation]["extendedEdges"].get(side)
                else:
                    extend[side] = self.dico[self.selectedItem]["extendedEdges"].get(side)
                    
            self.canvas.coords(self.canvas.elementsE[self.selectedItem],
            self.dico[self.selectedItem]["frame"]["x"] - extend["left"],
            self.dico[self.selectedItem]["frame"]["y"] - extend["top"], 
            self.dico[self.selectedItem]["frame"]["x"] + self.dico[self.selectedItem]["frame"]["width"] + extend["right"],
            self.dico[self.selectedItem]["frame"]["y"] + self.dico[self.selectedItem]["frame"]["height"] + extend["bottom"])


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

window.bind("<Button-3>", gui.popup)

window.bind("<+>", gui.changeSize)
window.bind("<minus>", gui.changeSize)


# window.bind("<MouseWheel>", gui.wheel)

mainloop()
