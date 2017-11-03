from Game.Utils import *
import Shared

class Figure:
    figType = None
    figClass = None
    player = 0
    position = None
    availActions = None
    id = -1

    def __init__(self, t, c, p, pos):
        self.figType = t
        self.figClass = c
        self.player = p
        self.position = pos
        self.availTurns = None

    def Act(self, pos, nextPos):
        if (self.availTurns == None):
            return False

        action = [pos, nextPos]
        own = Shared.ReallyEqual(self.position, pos)
        for key in self.availActions:
            if ((own and Shared.ReallyEqual(key, nextPos)) or (not own and Shared.ReallyEqual(key, action))):
                self.availActions = None
                return True

        self.availActions = None
        return False

    def AvailableTurns(self, field):
        self.availActions = self.figClass.AvailableTurns(self, field)
        return self.availActions

    def ResetAvailTurns(self):
        self.availActions = None

    def CellsNearby(self):
        return Shared.CellsNearby(self.position)
