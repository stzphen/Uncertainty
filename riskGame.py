from cmu_112_graphics import *
import random, string, math, time
from dataclasses import make_dataclass
import decimal
from riskMap import *
from riskAI import *
from riskInstructions import *
from PIL import ImageTk, Image

def gameMode_mousePressed(app, event):

    for continent in app.territories:
        for territory in app.territories[continent]:
            distance = math.sqrt((event.x - territory.x)**2 + (event.y - territory.y)**2)
            
            #checks if territory has been selected
            if distance <= app.radius2:
                
                if territory in app.player.bordering or territory in app.player.territories:
                    #checks what mode the game is in
                    if app.deployMode:
                        if territory in app.player.territories:
                            app.eventText = ""
                            app.current = (territory.continent, app.territories[territory.continent].index(territory))
                            app.player.formDeploy(app, territory)
                        else:
                            app.eventText = f"{continent} {territory.number} not in your territories!"

                    elif app.attackMode:
                        if app.player.attack == None and territory not in app.player.territories:
                            app.eventText = f"{continent} {territory.number} not in your territories!"
                        else:
                            app.eventText = ""
                            app.current = (continent, territory.number - 1)
                            app.neighbors = findNeighbors(app, territory.continent, territory.number - 1)
                            app.player.formAttack(app, territory)

                    elif app.moveMode:
                        if app.player.move == None and territory not in app.player.territories:
                            app.eventText = f"{continent} {territory.number} not in your territories!"
                        else:
                            app.eventText = ""
                            app.current = (continent, territory.number - 1)
                            app.neighbors = findNeighbors(app, territory.continent, territory.number - 1)
                            app.player.formMove(app, territory)
                    
                    else:
                        if territory.owner != None:
                            app.eventText = f"{continent} {territory.number} ({territory.owner.name}): {territory.troops} troops"
                        else:
                            app.eventText = f"{continent} {territory.number} (unclaimed): {territory.troops} troops"
                
                else:
                    if app.deployMode:
                        app.eventText = f"{continent} {territory.number} not in your territories!"
                    elif app.attackMode or app.moveMode:
                        app.eventText = f"{continent} {territory.number} not in bordering!"
                    else:
                        app.eventText = f"{continent} {territory.number}"

#states territory if hovering over it
def gameMode_mouseMoved(app, event):
    for continent in app.territories:
        for territory in app.territories[continent]:
            distance = math.sqrt((event.x - territory.x)**2 + (event.y - territory.y)**2)
            
            #checks if territory has been selected
            if distance <= app.radius2:
                app.eventText = f"{territory.continent} {territory.number}"            

def gameMode_keyPressed(app, event):

    #restarts game
    if event.key == "r":
        gameStarted(app)

    #activates deploy mode
    if event.key == "d":
        app.deployMode = True
        app.attackMode = False
        app.moveMode = False

    #activates attack mode
    if event.key == "a":
        app.attackMode = True
        app.deployMode = False
        app.moveMode = False

    #activates move mode
    if event.key == "m":
        app.moveMode = True
        app.deployMode = False
        app.attackMode = False
    
    #starts the playing of the moves
    if event.key == "p":
        app.moveMode = False
        app.deployMode = False
        app.attackMode = False

        app.startTurn = True
        app.showMoves = True

    #does a step
    if event.key == "Enter":
        if app.startTurn:
            doStep(app)
            checkWin(app)
    
    #forfeit
    if event.key == "f":
        gameOver(app, "loss")
    
    #autowin
    if event.key == "w":
        gameOver(app, "win")
    
    #get to instructions page
    if event.key == "i":
        app.mapBackground = app.mapBackground.resize((app.width, app.height))
        app.mode = "instructionsMode"

    #sets it to "standard mode" aka just checking the territories
    if event.key == "s":
        app.moveMode = False
        app.deployMode = False
        app.attackMode = False
    
    if event.key == "h":
        app.cheat = not app.cheat
    
    if event.key == "l":
        app.letsgo = not app.letsgo
    
    app.neighbors = set()
    app.current = tuple()

def doStep(app):

    #checks to see if this is the first move or end
    if app.step == 0:
        #if this is the first move
        if app.showMoves:
            #form moves of the ais and deploys troops
            for i in range(app.ai1.troops):
                app.ai1.formDeploy(app)
            for j in range(app.ai2.troops):
                app.ai2.formDeploy(app)
            
            app.ai1.formMoves(app)
            app.ai2.formMoves(app)
            
            app.player.deployTroops(app)
            app.ai1.deployTroops(app)
            app.ai2.deployTroops(app)

            app.deployDone = True

            app.step += 1

        #this is for the end and to reset for the next turn
        else:
            app.moveMode = False
            app.deployMode = False
            app.attackMode = False

            app.player.findTroops(app)
            app.ai1.findTroops(app)
            app.ai2.findTroops(app)
            
            app.player.formDeployOrdersFramework(app)
            app.ai1.formDeployOrdersFramework(app)
            app.ai2.formDeployOrdersFramework(app)
            
            app.showMoves = False
            app.deployDone = False
            app.startTurn = False
    
    #if its not first or last, it just does one of the steps
    else:
        performAttacksAndMoves(app, app.player.orders, app.ai1.orders, app.ai2.orders, app.step - 1)


#do the steps
def performAttacksAndMoves(app, playerMoves, ai1Moves, ai2Moves, step):
    combined = sorted([playerMoves, ai1Moves, ai2Moves], key = len)

    app.player.done = True
    app.ai1.done = True
    app.ai2.done = True
    
    if len(combined[0]) != 0:
        doAttackMove(app, combined[0][step])
        if combined[0][step][0].owner == combined[0][step][3]:
            combined[0][step][3].gameLogMoves.insert(0, combined[0][step])
            combined[0][step][3].done = False
        combined[0].pop(step)
    
    if len(combined[1]) != 0:
        doAttackMove(app, combined[1][step])
        if combined[1][step][0].owner == combined[1][step][3]:
            combined[1][step][3].gameLogMoves.insert(0, combined[1][step])
            combined[1][step][3].done = False
        combined[1].pop(step)
    
    if len(combined[2]) != 0:
        doAttackMove(app, combined[2][step])
        if combined[2][step][0].owner == combined[2][step][3]:
            combined[2][step][3].gameLogMoves.insert(0, combined[2][step])
            combined[2][step][3].done = False
        combined[2].pop(step)

    #checks if it is over, and puts out the dashes in the game log to signify end
    elif step == len(combined[2]):
        app.step = 0
        app.player.gameLogMoves.insert(0, "----------------------------")
        app.ai1.gameLogMoves.insert(0, "----------------------------")
        app.ai2.gameLogMoves.insert(0, "----------------------------")

        app.player.formDeployOrdersFramework(app)
        app.ai1.formDeployOrdersFramework(app)
        app.ai2.formDeployOrdersFramework(app)

        app.eventText = ""
        
        app.showMoves = False


#determins if it is attack or move
def doAttackMove(app, instructions):
    if instructions[1] == "attack":
        attack(app, instructions[3], instructions[0], instructions[2])

    else:
        move(app, instructions[3], instructions[0], instructions[2])


def attack(app, player, predator, prey):

    if predator.owner == player and prey.owner != player:
    #checks to see if attack takes over that territory
        if predator.troops >= prey.troops * 2:
            predator.troops = predator.troops - (prey.troops // 2)
            prey.troops = 0

        #checks to see if attack is a loss for the attacker
        elif predator.troops < prey.troops:
            prey.troops = prey.troops - (predator.troops // 2)
            predator.troops = 0

        #checks to see if attack is neither win nor loss, but both lose troops
        else:
            temp = prey.troops
            prey.troops = prey.troops - (predator.troops // 2)
            predator.troops = predator.troops - (temp // 2)

        #if it is a win, gives the new territory to attacker
        if prey.troops == 0:
            if prey.owner != None:
                prey.owner.territories.remove(prey)
            prey.troops = predator.troops
            predator.troops = 0
            player.territories.add(prey)
            prey.owner = player
            if prey.owner == app.player:
                app.eventText = f"You took {prey.continent} {app.territories[prey.continent].index(prey) + 1}!"
        
        #changes event text if attack occurs but no one wins
        elif prey.troops != 0 and prey.owner == app.player:
            app.eventText = f"You attacked {prey.continent} {app.territories[prey.continent].index(prey) + 1}!"

    #if the territory that is being attacked is now owned by the player, changes the attack to a move
    elif predator.owner == player and prey.owner == player:
        move(app, player, predator, prey)

    app.neighbors = set()
    app.current = tuple()
    player.bordering = set()
    app.player.findBorderingTerritories(app)


def move(app, player, predator, prey):

    #makes sure that the move occurs between two territoires owned by same player
    if predator.owner == player and prey.owner == player:
        temp = predator.troops
        prey.troops = predator.troops + prey.troops
        predator.troops = 0

        app.neighbors = set()
        app.current = tuple()
        player.bordering = set()
        app.player.findBorderingTerritories(app)
        #only prints eventText if it is the app.player
        if prey.owner == app.player:
            app.eventText = f"You moved {temp} troops to {prey.continent} {app.territories[prey.continent].index(prey) + 1}!"
    
    #changes move to attack if the prey is no longer owned by same player
    elif predator.owner == player and prey.owner != player:
        attack(app, player, predator, prey)

#checks for win or loss (from player's perspective)
def checkWin(app):
    if len(app.player.territories) == 42:
        gameOver(app, "win")
    if len(app.ai1.territories) == 42 or len(app.ai2.territories) == 42:
        gameOver(app, "loss")

#helps draw the win or loss
def gameOver(app, WoL):
    if WoL == "win":
        app.win = True
    else:
        app.loss = True
        

#hard coded a dictionary of all territories and their neighbors
def findNeighbors(app, continent, number):
    neighbors = {
                ("N. America", 0): {("N. America", 1), ("N. America", 5), ("Asia", 5)},
                ("N. America", 1): {("N. America", 0), ("N. America", 5), ("N. America", 6), ("N. America", 8)},
                ("N. America", 2): {("N. America", 3), ("N. America", 8), ("S. America", 3)},
                ("N. America", 3): {("N. America", 2), ("N. America", 6), ("N. America", 7), ("N. America", 8)},
                ("N. America", 4): {("N. America", 5), ("N. America", 6), ("N. America", 7), ("Europe", 1)},
                ("N. America", 5): {("N. America", 0), ("N. America", 1), ("N. America", 4), ("N. America", 6)},
                ("N. America", 6): {("N. America", 1), ("N. America", 3), ("N. America", 4), ("N. America", 5), ("N. America", 7), ("N. America", 8)},
                ("N. America", 7): {("N. America", 3), ("N. America", 4), ("N. America", 6)},
                ("N. America", 8): {("N. America", 1), ("N. America", 2), ("N. America", 3), ("N. America", 6)},
                ("S. America", 0): {("S. America", 1), ("S. America", 2)},
                ("S. America", 1): {("S. America", 0), ("S. America", 2), ("S. America", 3), ("Africa", 4)},
                ("S. America", 2): {("S. America", 0), ("S. America", 1), ("S. America", 2), ("S. America", 3)},
                ("S. America", 3): {("N. America", 2), ("S. America", 1), ("S. America", 2)},
                ("Europe", 0): {("Europe", 1), ("Europe", 2), ("Europe", 3), ("Europe", 6)},
                ("Europe", 1): {("N. America", 4), ("Europe", 0), ("Europe", 3)},
                ("Europe", 2): {("Europe", 0), ("Europe", 3), ("Europe", 4), ("Europe", 5), ("Europe", 6)},
                ("Europe", 3): {("Europe", 0), ("Europe", 1), ("Europe", 2), ("Europe", 5)},
                ("Europe", 4): {("Europe", 2), ("Europe", 5), ("Europe", 6), ("Africa", 2), ("Africa", 4), ("Asia", 6)},
                ("Europe", 5): {("Europe", 2), ("Europe", 3), ("Europe", 4), ("Asia", 0), ("Asia", 6), ("Asia", 10)},
                ("Europe", 6): {("Europe", 0), ("Europe", 2), ("Europe", 4), ("Africa", 4)},
                ("Africa", 0): {("Africa", 1), ("Africa", 4), ("Africa", 5)},
                ("Africa", 1): {("Africa", 0), ("Africa", 2), ("Africa", 3), ("Africa", 4), ("Africa", 5), ("Asia", 6)},
                ("Africa", 2): {("Europe", 4), ("Africa", 1), ("Africa", 4), ("Asia", 6)},
                ("Africa", 3): {("Africa", 1), ("Africa", 5)},
                ("Africa", 4): {("S. America", 1), ("Europe", 4), ("Europe", 6), ("Africa", 0), ("Africa", 1), ("Africa", 2)},
                ("Africa", 5): {("Africa", 0), ("Africa", 1), ("Africa", 3)},
                ("Asia", 0): {("Europe", 5), ("Asia", 1), ("Asia", 2), ("Asia", 6), ("Asia", 10)},
                ("Asia", 1): {("Asia", 0), ("Asia", 2), ("Asia", 7), ("Asia", 8), ("Asia", 9), ("Asia", 10)},
                ("Asia", 2): {("Asia", 0), ("Asia", 1), ("Asia", 6), ("Asia", 8)},
                ("Asia", 3): {("Asia", 5), ("Asia", 7), ("Asia", 9), ("Asia", 11)},
                ("Asia", 4): {("Asia", 5), ("Asia", 7)},
                ("Asia", 5): {("N. America", 0), ("Asia", 3), ("Asia", 4), ("Asia", 7), ("Asia", 11)},
                ("Asia", 6): {("Europe", 4), ("Europe", 5), ("Africa", 1), ("Africa", 2), ("Asia", 0), ("Asia", 2)},
                ("Asia", 7): {("Asia", 1), ("Asia", 3), ("Asia", 4), ("Asia", 5), ("Asia", 9)},
                ("Asia", 8): {("Asia", 1), ("Asia", 2), ("Australia", 1)},
                ("Asia", 9): {("Asia", 1), ("Asia", 3), ("Asia", 7), ("Asia", 10), ("Asia", 11)},
                ("Asia", 10): {("Europe", 5), ("Asia", 0), ("Asia", 1), ("Asia", 9)},
                ("Asia", 11): {("Asia", 3), ("Asia", 5), ("Asia", 9)},
                ("Australia", 0): {("Australia", 2), ("Australia", 3)},
                ("Australia", 1): {("Asia", 8), ("Australia", 2), ("Australia", 3)},
                ("Australia", 2): {("Australia", 0), ("Australia", 1), ("Australia", 3)},
                ("Australia", 3): {("Australia", 0), ("Australia", 1), ("Australia", 2)}
                }
    return neighbors[(continent, number)]
            

