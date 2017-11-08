from Game.Utils.NegArray import NegArray
from Game.Utils.Exceptions import ActionImpossible
from Game.Settings.Figures.FigureTypes import FigureType
import Shared

class GameState:
    def __init__(self, settings):
        self.field = NegArray(2)
        self.figures = {}
        self.limitations = settings.limitations
        self.availFigures = settings.figures
        self.availActions = [{},{}]
        self.availPlacements = [[],[]]
        self.turn = 0
        self.figId = 0
        self.lastMoved = None
        self.queens = [None, None]
        self.hasLost = [False, False]
        self.gameEnded = False
        for fig in self.availFigures[0]:
            canBeUsed = True
            act = (fig, (0, 0))
            for lim in self.limitations:
                if (not lim(self, 0, fig)):
                    canBeUsed = False
                    break
            if canBeUsed:
                self.availPlacements[0].append(act)

    def Get(self, pos):
        return self.field.Get(pos)

    def Put(self, figure):
        if (figure.id < 0):
            self.figId += 1
            figure.id = self.figId
            self.figures[figure.id] = figure

        return self.field.Put([figure], figure.position)

    def Remove(self, pos):
        return self.field.Put(None, pos)

    def Place(self, player, act):
        if (player != self.turn % 2):
            raise ActionImpossible("Wrong player turn")

        if (self.gameEnded):
            raise ActionImpossible("The game has already ended")

        canBeDone = False
        for key in self.availPlacements[player]:
            if (Shared.ReallyEqual(key, act)):
                canBeDone = True
                break

        if not canBeDone:
            raise ActionImpossible("Specified placement is impossible")

        self.figId += 1
        fig = act[0].GetFigure(player, act[1])
        fig.id = self.figId
        self.lastMoved = fig
        self.Put(fig)
        self.availFigures[player].remove(act[0])
        self.figures[fig.id] = fig
        self.RefreshPossibilities()

        if (act[0] == FigureType.Queen):
            self.queens[player] = fig

        self.turn += 1
        return fig.id

    def Move(self, player, id, f, t):
        if (player != self.turn % 2):
            raise ActionImpossible("Wrong player turn")

        if (self.gameEnded):
            raise ActionImpossible("The game has already ended")

        actions = self.availActions[player].get(id)
        if (actions == None):
            raise ActionImpossible("Action is impossible")
        figure = self.figures[id]
        if not figure.Act(f, t):
            raise ActionImpossible("Action is impossible")

        place = self.Get(f)
        it = place.pop(0)
        if len(place) == 0:
            self.Remove(f)

        moveTo = self.Get(t)
        if moveTo != None:
            moveTo.insert(0, it)
        else:
            it.position = t
            self.Put(it)

        self.lastMoved = it
        self.RefreshPossibilities()
        self.turn += 1
        return it.id

    def Skip(self, player):
        if (player != self.turn % 2):
            raise ActionImpossible("Wrong player turn")

        if (self.gameEnded):
            raise ActionImpossible("The game has already ended")

        if (len(self.availPlacements[player]) + len(self.availPlacements[player])) > 0:
            raise ActionImpossible("Cannot skip turn if there are available actions")

        self.turn += 1
        self.lastMoved = None

        return True

    def RefreshPossibilities(self):
        self.availActions = [{}, {}]
        self.availPlacements = [[], []]
        placePos = [[],[]]

        for kvp in self.figures.items():
            if self.queens[kvp[1].player] != None and self.CheckIntegrity(kvp[1]):
                self.availActions[kvp[1].player][kvp[0]] = kvp[1].AvailableTurns(self)
            else:
                otherActions = kvp[1].AvailableOthers(self)
                if otherActions != None and len(otherActions) > 0:
                    self.availActions[kvp[1].player][kvp[0]] = otherActions
                else:
                    kvp[1].ResetAvailTurns()

            itemOnPos = self.Get(kvp[1].position)
            if (itemOnPos != None and itemOnPos[0] == kvp[1]):
                near = Shared.CellsNearby(kvp[1].position)
                for cell in near:
                    presence = self.CheckPlayerPresence(cell)
                    if (presence[0] != presence[1]):
                        id = kvp[1].player
                        if (self.turn == 0):
                            id = 1
                        placePos[id] = Shared.Union(placePos[id], [cell])

        for id in range(0,2):
            for fig in self.availFigures[id]:
                canBeUsed = True
                for lim in self.limitations:
                    if (not lim(self, id, fig)):
                        canBeUsed = False
                        break
                if canBeUsed:
                    for place in placePos[id]:
                        self.availPlacements[id].append((fig, place))

        for i in range(0, 2):
            q = self.queens[i]
            if (q == None):
                self.hasLost[i] = False
            else:
                self.hasLost[i] = True
                near = Shared.CellsNearby(q.position)
                for cell in near:
                    fig = self.Get(cell)
                    if (fig == None):
                        self.hasLost[i] = False
                        break

        self.gameEnded = self.hasLost[0] or self.hasLost[1]

        return True


    def CheckIntegrity(self, me):
        vals = []
        myPos = self.Get(me.position)
        if len(myPos) > 1:
            return myPos[0] == me

        for kvp in self.figures.items():
            itemOnPos = self.Get(kvp[1].position)
            if kvp[1] != me and itemOnPos != None and itemOnPos[0] == kvp[1]:
                vals.append(kvp[1])

        if (len(vals) == 0):
            return False

        queue = [vals.pop()]
        while (len(queue) > 0):
            cur = queue.pop(0)
            near = Shared.CellsNearby(cur.position)
            for cell in near:
                dat = self.Get(cell)
                if (dat != None and dat[0] in vals):
                    vals.remove(dat[0])
                    queue.append(dat[0])

        return len(vals) == 0

    def CheckPlayerPresence(self, pos):
        if (self.Get(pos) != None):
            return [True, True]
        near = Shared.CellsNearby(pos)
        rv = [False, False]
        for cell in near:
            pos = self.Get(cell)
            if (pos != None):
                rv[pos[0].player] = True
                if (rv[0] == rv[1]):
                    return rv

        return rv




