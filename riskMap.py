from cmu_112_graphics import *
import random, string, math, time
from dataclasses import make_dataclass
import decimal
from riskGame import *
from riskAI import *
from riskInstructions import *
from PIL import ImageTk, Image

'''
Draws the map, and the playing field the user plays on
'''

#creates class for the territory, with some key info
class Territory(object):
    def __init__(self, x, y, continent, number, fill, owner, troops):
        self.x = x
        self.y = y
        self.continent = continent
        self.number = number
        self.fill = fill
        self.owner = owner
        self.troops = troops

#all the things that needs to be reset at the beginning of each match
def gameStarted(app):
    app.player = Player(app.name, app)
    app.ai1 = AI("orange", "AI1", app)
    app.ai2 = AI("lawnGreen", "AI2", app)
    app.claimedTerritories = set()
    app.neighbors = set()
    app.current = tuple()
    app.legalMove = True
    app.currentTerritoryText = ""
    app.eventText = ""
    app.step = 0
    app.showMoves = False
    app.startTurn = False
    app.deployDone = False
    app.cheat = False
    app.win = False
    app.loss = False
    gameVisuals(app)
    createTerritories(app)
    gameMode(app)

#mainly for game visuals and resizing purposes
def gameVisuals(app):
    app.innerWidth = 1227
    app.innerHeight = 624
    app.radius = 9
    app.radius2 = 20
    app.map = app.map.resize((app.innerWidth, app.innerHeight))
    app.compass = app.compass.resize((207, 200))
    app.mapBackground = app.mapBackground.resize((app.innerWidth, app.innerHeight))

#more of the game related stuff that occurs at start
def gameMode(app):
    app.player.territories = set()
    app.player.bordering = set()

    app.player.assignTerritories(app)
    app.player.findBorderingTerritories(app)
    app.ai1.assignTerritories(app)
    app.ai2.assignTerritories(app)
    
    app.player.findTroops(app)
    app.ai1.findTroops(app)
    app.ai2.findTroops(app)

    app.deployMode = False
    app.attackMode = False
    app.moveMode = False


#creates the list of territories as a dictionary
def createTerritories(app):
    for continent in app.startPoints:
        i = 1
        for territory in app.startPoints[continent]:

            if i == 1:
                app.territories[continent] = [(Territory(x = territory[0], y = int((territory[1]/628)*app.innerHeight), 
                                                continent = continent, number = i, fill = None, owner = None, troops = 2))]
            
            else:
                app.territories[continent].append((Territory(x = territory[0], y = int((territory[1]/628)*app.innerHeight), 
                                                    continent = continent, number = i, fill = None, owner = None, troops = 2)))
            i += 1

def gameMode_redrawAll(app, canvas):
    createBackground(app, canvas)
    drawInstructions(app, canvas)
    drawBoxesAndNumbers(app, canvas)
    drawSides(app, canvas)
    if app.letsgo:
        dababy(app, canvas)

#draws background of game (map, color, and compsass)
def createBackground(app, canvas):
    canvas.create_image(app.innerWidth//2, app.innerHeight//2, image = ImageTk.PhotoImage(app.mapBackground))
    canvas.create_image(app.innerWidth//2, app.innerHeight//2, image = ImageTk.PhotoImage(app.map))
    canvas.create_image(int((110/1440)*app.width), app.innerHeight - int((110/780)*app.height), image = ImageTk.PhotoImage(app.compass))

def drawInstructions(app, canvas):
    canvas.create_text(app.width*7/8, app.height - 20, text = 'Press "i" for instructions!', font = "Palatino 14")

#draws the inidivudal boxes and numbers that are clicked on
#changes color based on what's going on
def drawBoxesAndNumbers(app, canvas):
    fontSize = int((14/1440)*app.width)
    for continent in app.territories:
        for territory in app.territories[continent]:
            
            if app.cheat:

                if territory in app.player.territories:
                    territory.fill = app.player.color
                
                elif territory in app.ai1.territories:
                    territory.fill = app.ai1.color

                elif territory in app.ai2.territories:
                    territory.fill = app.ai2.color

                #belongs to no one
                else:
                    territory.fill = "grey"
            
            else:
                #checks if territory is owned by player
                if territory in app.player.territories:
                    territory.fill = app.player.color

                #checks if territory is in the bordering
                elif territory in app.player.bordering:
                    #checks if it belongs to ai1 or ai2
                    if territory in app.ai1.territories:
                        territory.fill = app.ai1.color

                    elif territory in app.ai2.territories:
                        territory.fill = app.ai2.color

                    #belongs to no one
                    else:
                        territory.fill = "grey"
                
                #territory is not seen right now
                else:
                    territory.fill = "white"

                #if territory if clicked on
                if (continent, territory.number - 1) == app.current:
                    territory.fill = "green"
                
                if app.attackMode:
                    if (continent, territory.number - 1) in app.neighbors and territory.owner != app.territories[app.current[0]][app.current[1]].owner:
                        territory.fill = "red"

                if app.moveMode:
                    if (continent, territory.number - 1) in app.neighbors and territory.owner == app.territories[app.current[0]][app.current[1]].owner:
                        territory.fill = "blue"

            #determins if move has started or not
            if app.showMoves:
                shownTroops = territory.troops
            else:
                try:
                    shownTroops = territory.troops + territory.owner.deployOrders[territory]
                except:
                    shownTroops = territory.troops

            if territory.fill != "white":
                canvas.create_rectangle(territory.x - app.radius, 
                                        territory.y - app.radius,
                                        territory.x + app.radius, 
                                        territory.y + app.radius,
                                        fill = territory.fill)
                canvas.create_text(territory.x, territory.y, 
                                    text = f"{shownTroops}", 
                                    font = f"Palatino {fontSize}")
        
            else:
                canvas.create_rectangle(territory.x - app.radius, 
                                    territory.y - app.radius,
                                    territory.x + app.radius, 
                                    territory.y + app.radius,
                                    fill = territory.fill)

#draws arrows for each move
def drawArrows(app, canvas, predator, prey, color):
    if (predator.continent, predator.number) == ("N. America", 1) and (prey.continent, prey.number) == ("Asia", 6):
        canvas.create_line(predator.x - 20, predator.y, 0, predator.y, width = 3,
                        fill = color)
        canvas.create_line(app.innerWidth, prey.y, prey.x + 20, prey.y, width = 3, arrow = LAST,
                        fill = color)
    elif (prey.continent, prey.number) == ("N. America", 1) and (predator.continent, predator.number) == ("Asia", 6):
        canvas.create_line(predator.x + 20, predator.y, app.innerWidth, predator.y, width = 3,
                        fill = color)
        canvas.create_line(0, prey.y, prey.x - 20, prey.y, width = 3, arrow = LAST,
                        fill = color)
    else:
        xDistance = (prey.x - predator.x)
        yDistance = (prey.y - predator.y)
        startX = predator.x + (xDistance / 5)
        startY = predator.y + (yDistance / 5)
        endX = prey.x - (xDistance / 5)
        endY = prey.y - (yDistance / 5)
        canvas.create_line(startX, startY, endX, endY, width = 3, arrow = LAST,
                            fill = color)

#draws the boxes on the side
def drawSides(app, canvas):
    playerMenu(app, canvas)
    ai1Menu(app, canvas)
    a12Menu(app, canvas)
    bottom(app, canvas)
    gameLogPlayer(app, canvas)
    gameLogAI1(app, canvas)
    gameLogAI2(app, canvas)

    if app.win or app.loss:
        drawEndgame(app, canvas)

#draws all text on players side
def playerMenu(app, canvas):
    
    canvas.create_rectangle(app.innerWidth, 0, app.width, 
                            app.innerHeight*15//16, fill = app.player.color)

    canvas.create_text(app.innerWidth + (app.width-app.innerWidth)/2, 20, 
                        text = f"{app.player.name}", 
                        font = "Palatino 22 bold")
    
    #shows how many troops you need to deploy
    if app.startTurn:
        canvas.create_text(app.innerWidth + (app.width-app.innerWidth)/2, 50, 
                        text = f"Troops to Deploy: {app.player.troops}",
                        font = "Palatino 15 bold")
    else:
        canvas.create_text(app.innerWidth + (app.width-app.innerWidth)/2, 50, 
                        text = f"Troops to Deploy: {app.player.troops - sum(app.player.deployOrders.values())}",
                        font = "Palatino 15 bold")
    
    textHeight = 80
    textDifference = 25

    if textHeight <= app.innerHeight*7//8:
        canvas.create_text(app.innerWidth + (app.width-app.innerWidth)/2, textHeight, 
                            text = "Deployment Orders",
                            font = "Palatino 15 bold")
    
    textHeight += textDifference + 5
    
    #writes out your deployment orders
    if not app.deployDone:

        for deployment in app.player.deployOrders:

            if textHeight <= app.innerHeight*7//8:
                if app.player.deployOrders[deployment] != 0:
                    canvas.create_text(app.innerWidth + 10, textHeight,
                                    text = f"Deploy {app.player.deployOrders[deployment]} troops to {deployment.continent} {deployment.number}",
                                    font = "Palatino 14", anchor = W)
                    textHeight += textDifference
    
        textHeight += 5

    canvas.create_text(app.innerWidth + (app.width-app.innerWidth)/2, textHeight, 
                        text = "Attack/Movement Orders",
                        font = "Palatino 15 bold")
    
    textHeight += textDifference + 5
    
    #writes out all attack/move orders
    for order in app.player.orders:

        if textHeight <= app.innerHeight*7//8:
            if order[1] == "attack":
                keyText = "attacks"
            
            else:
                keyText = "moves to"
            
            canvas.create_text(app.innerWidth + 10, textHeight,
                                text = f"{order[0].continent} {order[0].number} {keyText} {order[2].continent} {order[2].number}",
                                font = "Palatino 14", anchor = W)
            textHeight += textDifference


#shows the ai menus
def ai1Menu(app, canvas):

    canvas.create_rectangle(app.innerWidth, app.innerHeight*15//16, 
                            (app.innerWidth + app.width)/2, 
                            app.innerHeight, fill = app.ai1.color)

    canvas.create_text(app.innerWidth + (app.width - app.innerWidth)/4, 
                        app.innerHeight*31//32, text = "AI1", 
                        font = "Palatino 22 bold")

def a12Menu(app, canvas):

    canvas.create_rectangle((app.innerWidth + app.width)/2, 
                            app.innerHeight*15//16, app.width, 
                            app.innerHeight, fill = app.ai2.color)

    canvas.create_text(app.innerWidth + (app.width - app.innerWidth)*3/4, 
                        app.innerHeight*31//32, text = "AI2", 
                        font = "Palatino 22 bold")

def bottom(app, canvas):
    canvas.create_rectangle(app.width*3/4, app.innerHeight, app.width, 
                            app.height)
    canvas.create_text(app.width*7/8, app.innerHeight + (app.height - app.innerHeight)/2,
                        text = app.eventText, font = "Palatino 18 bold")

def gameLogPlayer(app, canvas):
    textHeight = app.innerHeight + 17
    textDifference = 25

    canvas.create_rectangle(0, app.innerHeight, app.width/4, 
                            app.height, fill = app.player.color)
    canvas.create_text(app.width/8, textHeight,  
                        text = f"{app.player.name} Game Log", font = "Palatino 18 bold")

    for move in app.player.gameLogMoves:
        textHeight += textDifference

        if move[1] == "deploy":
            canvas.create_text(app.width/8, textHeight,  
                            text = f"Deploy {move[4]} troops to {move[0].continent} {move[0].number}", font = "Palatino 12")
        elif move[1] == "attack":
            canvas.create_text(app.width/8, textHeight,  
                            text = f"{move[0].continent} {move[0].number} attacked {move[2].continent} {move[2].number}", font = "Palatino 12")
            if move == app.player.gameLogMoves[0] and not app.player.done:
                drawArrows(app, canvas, move[0], move[2], "red")
        elif move[1] == "move":
            canvas.create_text(app.width/8, textHeight,  
                            text = f"Moved troops from {move[0].continent} {move[0].number} to {move[2].continent} {move[2].number}", font = "Palatino 12")
            if move == app.player.gameLogMoves[0] and not app.player.done:
                drawArrows(app, canvas, move[0], move[2], "blue")
        else:
            canvas.create_text(app.width/8, textHeight,
                                text = move, font = "Palatino 12")

def gameLogAI1(app, canvas):
    textHeight = app.innerHeight + 17
    textDifference = 25

    canvas.create_rectangle(app.width/4, app.innerHeight, app.width/2, 
                            app.height, fill = app.ai1.color)
    canvas.create_text(app.width*3/8, textHeight, 
                        text = "AI1 Game Log", font = "Palatino 18 bold")
    
    for move in app.ai1.gameLogMoves:

        if move[0] in app.player.bordering or move[2] in app.player.bordering:
            textHeight += textDifference
            
            if move[1] == "deploy":
                canvas.create_text(app.width*3/8, textHeight,  
                                text = f"Deploy {move[4]} troops to {move[0].continent} {move[0].number}", font = "Palatino 12")
            elif move[1] == "attack":
                canvas.create_text(app.width*3/8, textHeight,  
                                text = f"{move[0].continent} {move[0].number} attacked {move[2].continent} {move[2].number}", font = "Palatino 12")
                if move == app.ai1.gameLogMoves[0] and not app.ai1.done:
                    drawArrows(app, canvas, move[0], move[2], "red")
            elif move[1] == "move forwards" or move[1] == "move backwards":
                canvas.create_text(app.width*3/8, textHeight,  
                                text = f"Moved troops from {move[0].continent} {move[0].number} to {move[2].continent} {move[2].number}", font = "Palatino 12")
                if move == app.ai1.gameLogMoves[0] and not app.ai1.done:
                    drawArrows(app, canvas, move[0], move[2], "blue")

        elif type(move) == str:
            textHeight += textDifference
            canvas.create_text(app.width*3/8, textHeight,
                                text = move, font = "Palatino 12")


def gameLogAI2(app, canvas):
    textHeight = app.innerHeight + 17
    textDifference = 25

    canvas.create_rectangle(app.width/2, app.innerHeight, app.width*3/4, 
                            app.height, fill = app.ai2.color)
    canvas.create_text(app.width*5/8, textHeight, 
                        text = "AI2 Game Log", font = "Palatino 18 bold")

    for move in app.ai2.gameLogMoves:
        if move[0] in app.player.bordering or move[2] in app.player.bordering:
            textHeight += textDifference

            if move[1] == "deploy":
                canvas.create_text(app.width*5/8, textHeight,  
                                text = f"Deploy {move[4]} troops to {move[0].continent} {move[0].number}", font = "Palatino 12")
            elif move[1] == "attack":
                canvas.create_text(app.width*5/8, textHeight,  
                                text = f"{move[0].continent} {move[0].number} attacked {move[2].continent} {move[2].number}", font = "Palatino 12")
                if move == app.ai2.gameLogMoves[0] and not app.ai2.done:
                    drawArrows(app, canvas, move[0], move[2], "red")
            elif move[1] == "move forwards" or move[1] == "move backwards":
                canvas.create_text(app.width*5/8, textHeight,  
                                text = f"Moved troops from {move[0].continent} {move[0].number} to {move[2].continent} {move[2].number}", font = "Palatino 12")
                if move == app.ai2.gameLogMoves[0] and not app.ai2.done:
                    drawArrows(app, canvas, move[0], move[2], "blue")

        elif type(move) == str:
            textHeight += textDifference
            canvas.create_text(app.width*5/8, textHeight,
                                text = move, font = "Palatino 12")

def drawEndgame(app, canvas):
    if app.win:
        endText = "You Won!"
        fill = "skyBlue1"
    if app.loss:
        endText = "You Lost"
        fill = "pink"
    canvas.create_rectangle(app.width/2 - 200, app.height/2 - 100,
                            app.width/2 + 200, app.height/2 + 100,
                            fill = fill)
    canvas.create_text(app.width/2, app.height/2 - 10, text = endText,
                            font = "Palatino 36 bold")

    canvas.create_text(app.width/2, app.height/2 + 60,
                        text = "Press r to restart",
                        font = "Palatino 16")

def dababy(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image = ImageTk.PhotoImage(app.dababy))
