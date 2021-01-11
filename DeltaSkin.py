# 

from tkinter import *
from tkinter import ttk
import time
import json
import easygui
from pdf2image import convert_from_path
import os

def chooseSize():
    size = input("Choose the screen size you want to change\n1- standard\n2- edgeToEdge\n")

    if size == "1":
        return "standard"
    elif size == "2":
        return "edgeToEdge"
    else:
        print('Selection failed!')
        chooseSize()

def chooseOrientation():
    size = input("Choose the screen size you want to change\n1- landscape\n2- portrait\n")

    if size == "1":
        return "landscape"
    elif size == "2":
        return "portrait"
    else:
        print('Selection failed!')
        chooseOrientation()

def printSkinInfo(skin):
    print('Name: {}\nConsole: {}\nSkin identifier: {}'.format(
    skin["name"], skin["gameTypeIdentifier"].split('.')[-1:][0],skin['identifier']
    ))

class Interface(Frame):

    def __init__(self, fenetre = None):
        self.fenetre = fenetre
        self.fenetre.title("Delta Skin Editor") #window title
        self.fenetre.resizable(False, False)

       # canvas object to create shape

        self.canvas = Canvas(fenetre,width=positions["representations"]["iphone"][size][orientation]['mappingSize']['width'],height=positions["representations"]["iphone"][size][orientation]['mappingSize']['height'])

        if positions["representations"]["iphone"][size][orientation]["assets"]["resizable"].split('.')[-1:][0] == "pdf":
            for page in convert_from_path(path + positions["representations"]["iphone"][size][orientation]["assets"]["resizable"], size=(positions["representations"]["iphone"][size][orientation]['mappingSize']['width'],positions["representations"]["iphone"][size][orientation]['mappingSize']['height'])):
                page.save('out.png', 'PNG')

            self.image = PhotoImage(file='out.png')
            self.canvas.background = self.canvas.create_image(0,0,image=self.image,anchor=NW)

        else:
            self.image = PhotoImage(file=path + positions["representations"]["iphone"][size][orientation]["assets"]["resizable"])
            self.canvas.background = self.canvas.create_image(0,0,image=self.image,anchor=NW)

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
            hor = 1
        elif press.keysym == "Left":
            hor = -1

        elif press.keysym == "Down":
            ver = 1
        elif press.keysym == "Up":
            ver = -1

        try:
            self.canvas.move(self.canvas.elements[self.selectedItem], hor, ver)
            self.canvas.move(self.canvas.elementsT[self.selectedItem], hor, ver)
            self.canvas.move(self.canvas.elementsE[self.selectedItem], hor, ver)

            self.dico[self.selectedItem]["frame"]["x"] += hor
            self.dico[self.selectedItem]["frame"]["y"] += ver

        except:
            print("error lol (prob nothing selected)")

    def scrapButtonsPos(self, json):
        self.dico = {}

        for elem in positions["representations"]["iphone"][size][orientation]["items"]:
            if len(elem["inputs"]) > 1:
                self.dico[str(elem["inputs"])] = elem
            else:
                self.dico[elem["inputs"][0]] = elem

    def collision(self, position):
        for key,item in self.dico.items():
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
        if positions["representations"]["iphone"][size][orientation].get("screens") != None:
            i=0
            for elem in positions["representations"]["iphone"][size][orientation]["screens"]:
                i+=1

                screenName = "screen" + "_" + str(i)

                self.dico[screenName] = {}
                self.dico[screenName]["frame"] = elem["outputFrame"]

                self.canvas.elements[screenName] = self.canvas.create_rectangle(self.dico[screenName]["frame"]["x"], self.dico[screenName]["frame"]["y"], self.dico[screenName]["frame"]["x"] + self.dico[screenName]["frame"]["width"], self.dico[screenName]["frame"]["y"] + self.dico[screenName]["frame"]["height"], fill = "yellow", stipple="gray50")
                self.canvas.elementsT[screenName] = self.canvas.create_text(self.dico[screenName]["frame"]["x"] + int(self.dico[screenName]["frame"]["width"]/2), self.dico[screenName]["frame"]["y"] + int(self.dico[screenName]["frame"]["height"]/2), text=screenName)
                self.canvas.elementsE[screenName] = self.canvas.create_rectangle(0,0,0,0) #just to avoid errors when moving
        else:
            print("No screens there")


    def save(self, osef):

        for elem in self.dico:
            if "screen_" in elem:
                positions["representations"]["iphone"][size][orientation]["screens"][int(elem.split('_')[-1]) - 1]["outputFrame"] = self.dico[elem]["frame"]
            else:
                i=0
                for truc in positions["representations"]["iphone"][size][orientation]["items"]:
                    positions["representations"]["iphone"][size][orientation]["items"][i]["inputs"]
                    i+=1

        with open(filepath, "w") as file:
            json.dump(file, positions, indent=2)
        print("Changes saved.")


filepath = easygui.fileopenbox()

with open(filepath, "r") as file:
    positions = json.load(file)
    path = file.split("\\")[:-1] #need to figure out what the hell this does
    path = "\\".join(path)
    path += "\\"

size = chooseSize()
orientation = chooseOrientation()

printSkinInfo(positions)

fenetre = Tk()
lol = Interface(fenetre)

fenetre.bind("<Button-1>", lol.collision)

fenetre.bind('<Left>', lol.move)
fenetre.bind('<Right>', lol.move)

fenetre.bind('<Up>', lol.move)
fenetre.bind('<Down>', lol.move)

fenetre.bind('<Control-s>', lol.save)

# fenetre.bind("<MouseWheel>", lol.wheel)

mainloop()
