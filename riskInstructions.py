from cmu_112_graphics import *
import random, string, math, time
from dataclasses import make_dataclass
import decimal
from riskMap import *
from riskAI import *
from riskGame import *
from PIL import ImageTk, Image

def instructionsMode_redrawAll(app, canvas):
    background(app, canvas)
    title(app, canvas)
    keys(app, canvas)
    instructions(app, canvas)
    returnText(app, canvas)
    objective(app, canvas)
    images(app, canvas)
    lines(app, canvas)

    if app.letsgo:
        dababy(app, canvas)

def instructionsMode_keyPressed(app, event):
    if app.gameStarted:
        app.mapBackground = app.mapBackground.resize((app.innerWidth, app.innerHeight))
        app.mode = "gameMode"
    else:
        app.mode = "startScreenMode"

def background(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image = ImageTk.PhotoImage(app.mapBackground))

def title(app, canvas):
    canvas.create_text(app.width/2, 60, text = 'How to Play "Uncertainty"', font = "Palatino 80 bold")

def objective(app, canvas):
    height = 180
    text = "Objective: conquer all territories and take over the world!"
    canvas.create_text(app.width/2, height, text = text,
                        font = "Palatino 50 bold")

def instructions(app, canvas):
    height = 275
    text = ["Click on a territory that you own to see what you can do!",
            'Press "d", "a", "m", to deploy, attack, or move your troops',
            "Look at your menu on the right to see your troops and moves",
            "Look at the bottom to see your game log and the AIs as well!",
            "The bottom right will keep you updates on what's going on",]
    for line in text:
        canvas.create_text(500, height, text = line, font = "Palatino 30")
        height += 50

def images(app, canvas):
    canvas.create_image(app.width*3/4 - 50, app.height/2, image = ImageTk.PhotoImage(app.i1))
    canvas.create_image(app.width/4, app.height*3/4, image = ImageTk.PhotoImage(app.i2))
    canvas.create_image(app.width*2/3 - 50, app.height*3/4 + 25, image = ImageTk.PhotoImage(app.i3))

def lines(app, canvas):
    canvas.create_line(95, 450, 77, 525, width = 2, arrow = LAST)
    canvas.create_line(750, 500, 895, 537, width = 2, arrow = LAST)
    canvas.create_line(914, 377, 943, 377, width = 2, arrow = LAST)

def keys(app, canvas):
    height = 300
    canvas.create_text(app.width - 300, height, text = "Keys to Know", font = "Palatino 40 bold",
                        anchor = W)
    height += 40
    text = ["D: Activate deploy mode",
            "A: Activate attack mode",
            "M: Activate move mode",
            "S: Activate standard mode",
            "H: See all territories",
            "P: Start playing",
            "Enter: See each turn",
            "F: Forfeit the game",
            "W: Autowin",
            "R: Restart"]
    for line in text:
        canvas.create_text(app.width - 300, height, text = line, font = "Palatino 20",
                            anchor = W)
        height += 30


def returnText(app, canvas):
    if app.gameStarted:
        canvas.create_text(app.width/2, app.height - 30, text = "Press any key to return to game", font = "Palatino 20")
    else:
        canvas.create_text(app.width/2, app.height - 30, text = "Press any key to return to start menu", font = "Palatino 20")

def dababy(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image = ImageTk.PhotoImage(app.dababy))