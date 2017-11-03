from Game.Utils.NegArray import NegArray
from Game.Utils.Exceptions import ActionImpossible
from Game.Settings.Figures.FigureTypes import FigureType
import Shared

class GameState:
    field = None
    figures = {}
    limitations = []
    availFigures = [[], []]
    availActions = [{}, {}]
    availPlacements = [[],[]]
    turn = 0
    figId = 0
    lastMoved = None
    canMove = [False, False]

    def __init__(self, settings):
        self.field = NegArray(2)
        self.availFigures = settings.figures
        self.limitations = settings.limitations
        for fig in self.availFigures[0]:
            canBeUsed = True
            act = (fig, (0, 0))
            for lim in self.limitations:
                if (not lim(self, act)):
                    canBeUsed = False
                    break
            if canBeUsed:
                self.availPlacements[0].append(act)

    def Get(self, pos):
        return self.field.Get(pos)

    def Put(self, figure, pos):
        self.figId += 1
        figure.id = self.figId
        self.figures[figure.id] = figure
        return self.field.Put([figure], pos)

    def Place(self, player, act):
        if (player != self.turn % 2):
            raise ActionImpossible("Wrong player turn")
        canBeDone = False
        for key in self.availPlacements[player]:
            if (Shared.ReallyEqual(key, act)):
                canBeDone = True

        if not canBeDone:
            raise ActionImpossible("Specified placement is impossible")

        self.figId += 1
        fig = act[0].GetFigure(player, act[1])
        fig.id = self.figId
        self.lastMoved = fig
        self.field.Put(fig, act[1])
        self.availFigures[player].remove(act[0])
        self.turn += 1
        self.figures[fig.id] = fig
        self.RefreshPossibilities()

        if (act[0] == FigureType.Queen):
            self.canMove[player] = True

    def Move(self, player, id, f, t):
        if (player != self.turn % 2):
            raise ActionImpossible("Wrong player turn")

        actions = self.availActions[player].get(id)
        if (actions == None):
            raise ActionImpossible("Action is impossible")
        figure = self.figures[id]
        if not figure.Act(f, t):
            raise ActionImpossible("Action is impossible")

        place = self.field.Get(f)
        it = place.pop(0)
        if len(place) == 0:
            self.field.Put(None, f)

        moveTo = self.field.Get(t)
        if moveTo != None:
            moveTo.insert(0, it)
        else:
            self.field.Put(it, t)

        it.position = t

        self.RefreshPossibilities()

    def RefreshPossibilities(self):
        self.availActions = [{}, {}]
        self.availPlacements = [[], []]

        for kvp in self.figures.items():
            if self.canMove[kvp[1].player] and self.CheckIntegrity(kvp[1]):
                self.availActions[kvp[1].player][kvp[0]] = kvp[1].AvailableTurns()
            else:
                kvp[1].ResetAvailTurns()

            if (self.field.Get(kvp[1].posiiton)[0] == kvp[1]):
                near = Shared.CellsNearby(kvp[1].position)
                for cell in near:
                    presence = self.CheckPlayerPresence(cell)
                    if (presence[0] != presence[1]):
                        id = 0
                        if (presence[1]):
                            id = 1
                        for fig in self.availFigures[id]:
                            canBeUsed = True
                            act = (fig, (0, 0))
                            for lim in self.limitations:
                                if (not lim(self, act)):
                                    canBeUsed = False
                                    break
                            if canBeUsed:
                                self.availPlacements[id].append(act)


    def CheckIntegrity(self, me):
        vals = []
        myPos = self.field.Get(me.position)
        if len(myPos) > 1:
            return myPos[0] == me

        for kvp in self.figures.items():
            if kvp[1] != me and self.field.Get(kvp[1].position)[0] == kvp[1]:
                vals.append(kvp[1])

        if (len(vals) == 0):
            return False

        queue = [vals.pop()]
        while (len(queue) > 0):
            cur = queue.pop(0)
            near = Shared.CellsNearby(cur.position)
            for cell in near:
                dat = self.field.Get(cell)
                if (dat != None and dat[0] in vals):
                    vals.remove(dat[0])
                    queue.append(dat[0])

        return len(vals) == 0

    def CheckPlayerPresence(self, pos):
        if (self.field.Get(pos) != None):
            return [True, True]
        near = Shared.CellsNearby(pos)
        rv = [False, False]
        for cell in near:
            pos = self.field.Get(cell)
            if (pos != None):
                rv[pos[0].player] = True
                if (rv[0] == rv[1]):
                    return rv

        return rv




