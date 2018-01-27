from ..Utils import *
from ... import Shared

class Figure:
    def __init__(self, t, c, p, pos):
        self.figType = t
        self.figClass = c
        self.player = p
        self.position = pos
        self.availActions = None
        self.id = -1
        self.layer = 0

    def __eq__(self, other):
        return (
            other is not None and
            self.id == other.id and
            self.figType == other.figType and
            self.figClass == other.figClass and
            self.position == other.position and
            self.layer == other.layer and
            self.player == other.player
        )

    def ToHash(self):
        return {
            "type": self.figType,
            "position": self.position,
            "layer": self.layer,
            "id": self.id
        }

    def Act(self, pos, nextPos):
        if (self.availActions == None):
            return False

        action = [pos, nextPos]
        own = Shared.ReallyEqual(self.position, pos)
        for key in self.availActions:
            if ((own and Shared.ReallyEqual(key, nextPos)) or (not own and Shared.ReallyEqual(key, action))):
                self.availActions = None
                return True

        return False

    def AvailableTurns(self, field):
        self.availActions = self.figClass.AvailableTurns(self, field)
        return self.availActions

    def AvailableOthers(self, field):
        self.availActions = None

        if self.figClass.canOthers:
            self.availActions = self.figClass.AvailableOthers(self, field)
            return self.availActions

        return None

    def ResetAvailTurns(self):
        self.availActions = None

    def CellsNearby(self):
        return Shared.CellsNearby(self.position)
