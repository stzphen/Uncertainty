from cmu_112_graphics import *
import random, string, math, time
from dataclasses import make_dataclass
import decimal
from riskGame import *
from riskAI import *
from riskMap import *
from riskInstructions import *
from PIL import ImageTk, Image


def appStarted(app):
    app.mode = "startScreenMode"
    app.startBackground = Image.open("startBackground.png")
    # https://www.pinterest.com/pin/799740846304983825/
    app.startBackground = app.startBackground.resize((app.width, app.height))

    app.mapBackground = Image.open("mapBackground.png")
    #https://wallpapercave.com/old-map-background

    app.letsgo = False
    app.dababy = Image.open("dababy.png")
    # https://media.pitchfork.com/photos/5c7d4c1b4101df3df85c41e5/1:1/w_320/Dababy_BabyOnBaby.jpg

    app.i1 = Image.open("i1.png")
    app.i2 = Image.open("i2.png")
    app.i3 = Image.open("i3.png")
    app.i1 = app.i1.resize((150, 250))
    app.i2 = app.i2.resize((600, 100))
    app.i3 = app.i3.resize((250, 125))

    #gameStart stuff
    app.gameStarted = False
    app.boxes = []
    app.map = Image.open("riskMap.png")
    # https://upload.wikimedia.org/wikipedia/commons/9/9d/Risk_game_map.png
    app.compass = Image.open("compass.png")
    # http://clipart-library.com/clipart/di45B8j6T.htm
    app.startPoints = { "N. America" : [(85, 75), (144, 116), (140, 252), (211, 190), (431, 41), (181, 72), (231, 121), (307, 122), (126, 176)],
                    "S. America": [(296, 510), (342, 415), (284, 436), (271, 334)],
                    "Europe": [(520, 126), (496, 88), (608, 133), (609, 88), (641, 168), (688, 121), (563, 167)],
                    "Africa": [(642, 365), (721, 329), (641, 239), (746, 451), (550, 281), (646, 454)],
                    "Asia": [(801, 160), (954, 213), (871, 259), (955, 120), (1113, 196), (1072, 78), (725, 210), (966, 160), (979, 291), (866, 75), (795, 97), (962, 74)],
                    "Australia": [(1140, 484), (1026, 365), (1145, 391), (1047, 490)]
                }
    app.territories = dict()

"""
Start Mode
"""

def startScreenMode_mousePressed(app, event):
    if app.height*3/4 - 60 <= event.y <= app.height*3/4 + 60:
        if app.width/3 - 150 <= event.x <= app.width/3 + 150:
            app.name = app.getUserInput("What is your player's name?")
            app.mode = "gameMode"
            app.gameStarted = True
            gameStarted(app)
        if app.width*2/3 - 150 <= event.x <= app.width*2/3 + 150:
            app.mapBackground = app.mapBackground.resize((app.width, app.height))
            app.mode = "instructionsMode"

def startScreenMode_keyPressed(app, event):
    if event.key == "l":
        app.letsgo = not app.letsgo

def startScreenMode_redrawAll(app, canvas):
    entranceImage(app, canvas)
    logo(app, canvas)
    buttons(app, canvas)
    if app.letsgo:
        dababy(app, canvas)

def entranceImage(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image = ImageTk.PhotoImage(app.startBackground))

def logo(app, canvas):
    canvas.create_text(app.width/2, app.height/2 - 75, text = "Uncertainty",
                    font = "Palatino 100 bold italic", fill = "white")

def buttons(app, canvas):
    startButton(app, canvas)
    instructions(app, canvas)

def startButton(app, canvas):
    canvas.create_rectangle(app.width/3 - 150, app.height*3/4 - 60,
                            app.width/3 + 150, app.height*3/4 + 60,
                            fill = "peachpuff", activefill = "salmon")
    canvas.create_text(app.width/3, app.height*3/4, text = "Play Now!",
                        font = "Palatino 34 bold")

def instructions(app, canvas): 
    canvas.create_rectangle(app.width*2/3 - 150, app.height*3/4 - 60,
                            app.width*2/3 + 150, app.height*3/4 + 60,
                            fill = "peachpuff", activefill = "salmon")
    canvas.create_text(app.width*2/3, app.height*3/4, text = "Instructions",
                        font = "Palatino 34 bold")

def dababy(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image = ImageTk.PhotoImage(app.dababy))

def main():
    runApp(width=1440, height=780)

if __name__ == '__main__':
    main()