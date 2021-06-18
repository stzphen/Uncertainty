from cmu_112_graphics import *
import random, string, math, time
from dataclasses import make_dataclass
import decimal
from riskGame import *
from riskMap import *
from riskInstructions import *
from PIL import ImageTk, Image

class AI(object):
    def __init__(self, color, name, app):
        self.color = color
        self.territories = set()
        self.name = name
        self.troops = 0
        self.deployOrders = dict()
        self.orders = []
        self.rankedOrders = []
        self.gameLogMoves = []
        self.done = True
    
    #assigns 5 random territories at beginning of game
    def assignTerritories(self, app):
        continent = random.choice(list(app.territories))
        newTerritory = random.choice(app.territories[continent])

        while len(self.territories) == 0:
            if newTerritory not in app.claimedTerritories:
                self.territories.add(newTerritory)
                newTerritory.owner = self
                newTerritory.troops = 0
                app.claimedTerritories.add(newTerritory)
        
        while len(self.territories) != 5:
        
            neighbors = self.findBorderingTerritories(app, random.choice(list(self.territories)))

            for place in neighbors:
                if place not in app.claimedTerritories:
                    self.territories.add(place)
                    place.owner = self
                    place.troops = 0
                    app.claimedTerritories.add(place)
                    if len(self.territories) == 5:
                        break
        
        self.formDeployOrdersFramework(app)
 
    #finds all bordering territories
    def findBorderingTerritories(self, app, territory):
        neighbors = findNeighbors(app, territory.continent, territory.number - 1)
        bordering = set()

        for place in neighbors:
            location = app.territories[place[0]][place[1]]
            if location not in bordering and location not in self.territories:
                bordering.add(location)
        return bordering
    
    #find territories that AI also owns that is bordering the selected one
    def findOwnBordering(self, app, territory):
        neighbors = findNeighbors(app, territory.continent, territory.number - 1)
        ownBorder = set()

        for place in neighbors:
            location = app.territories[place[0]][place[1]]
            if location not in ownBorder and location in self.territories:
                ownBorder.add(location)
        return ownBorder
    
    def findTroops(self, app):
        self.troops = 5 + len(self.territories)

    def formDeployOrdersFramework(self, app):
        self.deployOrders = dict()
        for territory in self.territories:
            self.deployOrders[territory] = 0

    def formDeploy(self, app):
        if self.troops - sum(self.deployOrders.values()) > 0:
            self.deployOrders[self.findMostHelp(app)] += 1
  
    # deploys troops based on which one needs most help
    def deployTroops(self, app):
        for territory in self.deployOrders:
            if self.deployOrders[territory] != 0:
                territory.troops += self.deployOrders[territory]
                self.troops -= self.deployOrders[territory]
                self.gameLogMoves.insert(0, (territory, "deploy", territory, self, self.deployOrders[territory]))

    # determines which territories need most help by looking at number of troops
    # how many "threatening" territories there are, and how many easy "wins"
    # are nearby
    def findMostHelp(self, app):
        mostHelpNeeded = None
        mostHelpNeededScore = 0

        for territory in self.territories:
            helpScore = -10
            
            #sees if there are any opponent territories, if none, then it doesn't even bother deploying there
            if self.findBorderingTerritories(app, territory) == set():
                pass

            else:
                helpScore = 0
                helpScore -= ((territory.troops + self.deployOrders[territory]))
                helpScore += (len(self.findOwnBordering(app, territory)) * 0.7)
                helpScore += (len(self.findLegitThreats(app, territory.continent, territory)) * 0.8)
                helpScore += (len(self.findEasyWins(app, territory.continent, territory)) * 0.8)
                helpScore += importanceOfTerritory(self, app, territory.continent, territory)

            if helpScore > mostHelpNeededScore:
                mostHelpNeeded = territory
                mostHelpNeededScore = helpScore

        if mostHelpNeeded == None:
            return list(self.territories)[0]
        
        else:
            return mostHelpNeeded

    #find a "legit threat", aka likely to attack and can beat you easily
    def findLegitThreats(self, app, continent, territory):
        threats = set()
        neighbors = self.findBorderingTerritories(app, territory)
        for place in neighbors:
            if (place.troops > (territory.troops + self.deployOrders[territory]) * 1.5 and place.owner != None
                and reasonToAttack(app, territory, self, place.troops)):
                    threats.add(place)
        return threats
        
    #find an "easy win", aka no troops deployed needed to win
    def findEasyWins(self, app, continent, territory):
        wins = set()
        neighbors = self.findBorderingTerritories(app, territory)
        for place in neighbors:
            if place.troops * 2 <= (territory.troops + self.deployOrders[territory]) or place.owner == None:
                wins.add(place)
        return wins
    
    #returns whether or not it should attack, and what territory it is attacking if attack occurs
    def attackOrNot(self, app, territory):

        # make sure attack
        neighbors = self.findBorderingTerritories(app, territory)
        ratio = 0
        bestRatio = 0
        bestPlace = None

        if neighbors == set():
            return (False, None)
        
        #needs to be fixed
        for place in neighbors:
            if (territory.troops + self.deployOrders[territory]) > 0:
                try:
                    ratio = (territory.troops + self.deployOrders[territory]) / place.troops
                except:
                    ratio = 10
            
            #tries to anticpate if new troops will be deployed
            if 0.5 < ratio < 1.8:
                ratio = (territory.troops + self.deployOrders[territory]) / (place.troops * 1.5)
            
            if ratio > bestRatio:
                bestRatio = ratio
                bestPlace = place

        if bestRatio < 1:
            return (False, None)

        return (True, bestPlace)


    # make sure to only check if territory has troops (0 troops --> don't check)
    def moveOrNot(self, app, territory):

        ownNeighbors = self.findOwnBordering(app, territory)
        otherNeighbors = self.findBorderingTerritories(app, territory)
        moveForwards = False
        moveBackwards = False

        if ownNeighbors == set() or territory.troops + self.deployOrders[territory] == 0:
            return (False, None)

        for place in otherNeighbors:
            if place.troops > (territory.troops + self.deployOrders[territory]) * 2:
                moveBackwards = True
        
        if moveBackwards:
            minTerritories = 1000000000000
            placeInQuestion2 = None
            for place4 in ownNeighbors:
                places = len(self.findBorderingTerritories(app, place4))
                if places < minTerritories:
                    placeInQuestion2 = place4
                    minTerritories = places
            return (True, placeInQuestion2, "backwards")
        
        for place2 in ownNeighbors:
            for place3 in self.findBorderingTerritories(app, place2):
                if place2.troops + (territory.troops + self.deployOrders[territory]) > 1.5 * place3.troops:
                    moveForwards = True
        
        if moveForwards:
            maxAdvantage = 0
            placeInQuestion3 = None
            for place5 in ownNeighbors:
                for place6 in self.findBorderingTerritories(app, place5):
                    try:
                        advantage = ((territory.troops + self.deployOrders[territory]) + place5.troops) / place6.troops
                    except:
                        advantage = 5
                    if advantage > maxAdvantage:
                        maxAdvantage = advantage
                        placeInQuestion3 = place5
            return (True, placeInQuestion3, "forwards")
        
        else:
            return (False, None)
    
    #forms the "orders"
    def formMoves(self, app):
        for territory in self.territories:
            if self.attackOrNot(app, territory)[0] == True:
                self.orders.append((territory, "attack", self.attackOrNot(app, territory)[1], self))
            elif self.moveOrNot(app, territory)[0] == True:
                self.orders.append((territory, "move" + " " + self.moveOrNot(app, territory)[2], self.moveOrNot(app, territory)[1], self))


    def determineUrgency(self, app):
        for move in self.orders:
            if move[1] == "move backwards":
                self.rankedOrders.append(move)
                self.orders.pop(move)
        
        for move in self.orders:
            if move[1] == "attack":
                self.rankedOrders.append(move)
                self.orders.pop(move)
        
        for move in self.orders:
            if move[1] == "move forwards":
                self.rankedOrders.append(move)
                self.orders.pop(move)

class Player(object):
    def __init__(self, name, app):
        self.name = name
        self.color = "cyan"
        self.territories = set()
        self.bordering = set()
        self.troops = 0
        self.deployOrders = dict()
        self.orders = []
        self.attack = None
        self.move = None
        self.gameLogMoves = []
        self.done = True
    
    def assignTerritories(self, app):
        continent = random.choice(list(app.territories))
        newTerritory = random.choice(app.territories[continent])

        while len(self.territories) == 0:
            if newTerritory not in app.claimedTerritories:
                self.territories.add(newTerritory)
                newTerritory.owner = self
                newTerritory.troops = 0
                app.claimedTerritories.add(newTerritory)
        
        while len(self.territories) != 5:
        
            neighbors = self.findBorderingSpecific(app, random.choice(list(self.territories)))

            for place in neighbors:
                if place not in app.claimedTerritories:
                    self.territories.add(place)
                    place.owner = self
                    place.troops = 0
                    app.claimedTerritories.add(place)
                    if len(self.territories) == 5:
                        break

        self.formDeployOrdersFramework(app)  
    
    def findBorderingTerritories(self, app):
        for territory in self.territories:
            neighbors = findNeighbors(app, territory.continent, territory.number - 1)
            for place in neighbors:
                location = app.territories[place[0]][place[1]]
                if location not in self.bordering and location not in self.territories:
                    self.bordering.add(location)
    
        #finds all bordering territories
    def findBorderingSpecific(self, app, territory):
        neighbors = findNeighbors(app, territory.continent, territory.number - 1)
        bordering = set()

        for place in neighbors:
            location = app.territories[place[0]][place[1]]
            if location not in bordering and location not in self.territories:
                bordering.add(location)
        return bordering
    
    def findOwnBorderingSpecific(self, app, territory):
        neighbors = findNeighbors(app, territory.continent, territory.number - 1)
        bordering = set()

        for place in neighbors:
            location = app.territories[place[0]][place[1]]
            if location not in bordering and location in self.territories:
                bordering.add(location)
        return bordering
    
    def findTroops(self, app):
        self.troops = 5 + len(self.territories)

    def formDeployOrdersFramework(self, app):
        self.deployOrders = dict()
        for territory in self.territories:
            self.deployOrders[territory] = 0

    def formDeploy(self, app, territory):
        if territory in self.territories:
            if self.troops - sum(self.deployOrders.values()) > 0:
                self.deployOrders[territory] += 1
            else:
                app.eventText = "All troops have been deployed!"
    
    def formAttack(self, app, territory):
        
        if self.attack == None:
            self.attack = territory
        
        else:
            if territory.owner != self and territory in self.findBorderingSpecific(app, self.attack):
                self.attack = (self.attack, "attack", territory, self)
                self.orders.append(self.attack)
            self.attack = None
            app.neighbors = set()
            app.current = tuple()
    
    def formMove(self, app, territory):

        if self.move == None:
            self.move = territory
        
        else:
            if territory.owner == self and territory in self.findOwnBorderingSpecific(app, self.move):
                self.move = (self.move, "move", territory, self)
                self.orders.append(self.move)
            self.move = None
            app.neighbors = set()
            app.current = tuple()
    
        # deploys troops based on which one needs most help
    def deployTroops(self, app):
        for territory in self.deployOrders:
            if self.deployOrders[territory] != 0:
                territory.troops += self.deployOrders[territory]
                self.troops -= self.deployOrders[territory]
                self.gameLogMoves.insert(0, (territory, "deploy", territory, self, self.deployOrders[territory]))

def importanceOfTerritory(player, app, continent, territory):

    ownBordering = player.findOwnBordering(app, territory)
    allBordering = player.findBorderingTerritories(app, territory)
    
    #finding bordering territories with reasonToAttack
    attackingTerritories = 0
    for place in allBordering:
        if place not in ownBordering and place.owner != None:
            if reasonToAttack(app, territory, player, place.troops):
                attackingTerritories += 1

    #find bordering territories that you'd want to attack
    prey = 0
    for place in allBordering:
        if place not in ownBordering:
            if territory.troops > place.troops or place.owner == None:
                prey += 1

    # number of troops in ownBordering
    borderingTroops = 0
    for terr in ownBordering:
        borderingTroops += terr.troops

    # total territories left
    fractionOfTotal = 1 / len(player.territories)

    # number of territories that you would be "exposing"
    exposed = len(ownBordering)

    if exposed > 0 and borderingTroops > 0:
        return fractionOfTotal * borderingTroops * exposed * ((attackingTerritories*2) + prey + 1)
    if borderingTroops > 0:
        return fractionOfTotal * borderingTroops * 0.9 * ((attackingTerritories*2) + prey + 1)
    if exposed > 0:
        return fractionOfTotal * 0.9 * exposed * ((attackingTerritories*2) + prey + 1)
    else:
        return fractionOfTotal * 0.9 * 0.9 * ((attackingTerritories*2) + prey + 1)

# tries to see if other person has a reason to attack your territory
def reasonToAttack(app, territory, player, opps):

    if territory.owner == None:
        return False

    if len(territory.owner.territories) < 3:
        return True

    ownBordering = player.findOwnBordering(app, territory)
    troops = 0
    for place in ownBordering:
        troops += place.troops

    if len(ownBordering) < 2 or opps > troops:
        return True
    return False
    # what other advantages do they get of attacking your territory? (entering new land?)

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

 