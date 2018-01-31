from collections import defaultdict

from .Settings.Figures.FigureTypes import FigureType
from .Utils.Exceptions import ActionImpossible
from .Utils.NegArray import NegArray
from .. import Shared


class GameState:
    def __init__(self, settings):
        self.field = NegArray(2)
        self.figures = {}
        self.limitations = settings.limitations
        self.availFigures = settings.figures
        self.availActions = [{}, {}]
        self.availPlacements = [[[], []], [[], []]]
        self.turn = 0
        self.figId = 0
        self.lastMoved = None
        self.queens = [None, None]
        self.hasLost = [False, False]
        self.gameEnded = False
        self.FillPlacementFigures(0)
        self.availPlacements[0][1].append((0, 0))

    def __eq__(self, other):
        return (
                self.field == other.field and
                self.figures == other.figures and
                self.limitations == other.limitations and
                self.availFigures == other.availFigures and
                self.turn == other.turn and
                self.figId == other.figId and
                self.lastMoved == other.lastMoved and
                self.hasLost == other.hasLost and
                self.gameEnded == other.gameEnded
        )

    def FillPlacementFigures(self, player_num):
        for fig in self.availFigures[player_num]:
            if fig not in self.availPlacements[player_num][0]:
                canBeUsed = True
                for lim in self.limitations:
                    if not lim(self, 0, fig):
                        canBeUsed = False
                        break
                if canBeUsed:
                    self.availPlacements[player_num][0].append(fig)

    def Get(self, pos):
        return self.field.Get(pos)

    def Put(self, figure):
        if figure.id < 0:
            self.figId += 1
            figure.id = self.figId
            self.figures[figure.id] = figure

        return self.field.Put([figure], figure.position)

    def Remove(self, pos):
        return self.field.Put(None, pos)

    def Place(self, player, figure, position):
        if player != self.turn % 2:
            raise ActionImpossible("Wrong player turn")

        if self.gameEnded:
            raise ActionImpossible("The game has already ended")

        canBeDone = False
        for key in self.availPlacements[player][1]:
            if Shared.ReallyEqual(key, position):
                canBeDone = True
                break

        if not canBeDone:
            raise ActionImpossible("Specified placement is impossible")

        if figure not in self.availPlacements[player][0]:
            raise ActionImpossible("Specified placement is not available")

        self.figId += 1
        fig = figure.GetFigure(player, position)
        fig.id = self.figId
        pos = self.Get(fig.position)
        if pos is not None:
            for key in pos:
                key.layer += 1
        fig.layer = 0
        self.lastMoved = fig
        self.Put(fig)
        self.availFigures[player].remove(figure)
        self.figures[fig.id] = fig
        self.RefreshPossibilities()

        if figure == FigureType.Queen:
            self.queens[player] = fig

        self.turn += 1
        return fig.id

    def Move(self, player, fid, f, t):
        if player != self.turn % 2:
            raise ActionImpossible("Wrong player turn")

        if self.gameEnded:
            raise ActionImpossible("The game has already ended")

        actions = self.availActions[player].get(fid)
        if actions is None:
            raise ActionImpossible("Action is impossible")
        figure = self.figures[fid]
        if not figure.Act(f, t):
            raise ActionImpossible("Action is impossible")

        place = self.Get(f)
        it = place.pop(0)
        if len(place) == 0:
            self.Remove(f)
        else:
            for key in place:
                key.layer -= 1

        it.position = t
        moveTo = self.Get(t)
        if moveTo is not None:
            for key in moveTo:
                key.layer += 1
            moveTo.insert(0, it)
        else:
            self.Put(it)

        it.layer = 0
        self.lastMoved = it
        self.RefreshPossibilities()
        self.turn += 1
        return it.id

    def Skip(self, player):
        if player != self.turn % 2:
            raise ActionImpossible("Wrong player turn")

        if self.gameEnded:
            raise ActionImpossible("The game has already ended")

        if (len(self.availPlacements[player][1]) * len(self.availPlacements[player][0]) + len(
                self.availActions[player])) > 0:
            raise ActionImpossible("Cannot skip turn if there are available actions")

        self.turn += 1
        self.lastMoved = None

        return True

    def RefreshPossibilities(self):
        self.availActions = [{}, {}]
        self.availPlacements = [[[], []], [[], []]]

        for kvp in self.figures.items():
            if self.queens[kvp[1].player] is not None and self.CheckIntegrity(kvp[1]):
                ac = kvp[1].AvailableTurns(self)
                if ac is not None and len(ac) > 0:
                    self.availActions[kvp[1].player][kvp[0]] = kvp[1].AvailableTurns(self)
                else:
                    kvp[1].ResetAvailTurns()
            else:
                otherActions = kvp[1].AvailableOthers(self)
                if otherActions is not None and len(otherActions) > 0:
                    self.availActions[kvp[1].player][kvp[0]] = otherActions
                else:
                    kvp[1].ResetAvailTurns()

            itemOnPos = self.Get(kvp[1].position)
            if itemOnPos is not None and itemOnPos[0] == kvp[1]:
                near = Shared.CellsNearby(kvp[1].position)
                for cell in near:
                    presence = self.CheckPlayerPresence(cell)
                    if presence[0] != presence[1]:
                        player_num = kvp[1].player
                        if self.turn == 0:
                            player_num = 1
                        self.availPlacements[player_num][1] = Shared.Union(self.availPlacements[player_num][1], [cell])

        self.FillPlacementFigures(0)
        self.FillPlacementFigures(1)

        for i in range(0, 2):
            q = self.queens[i]
            if q is None:
                self.hasLost[i] = False
            else:
                self.hasLost[i] = True
                near = Shared.CellsNearby(q.position)
                for cell in near:
                    fig = self.Get(cell)
                    if fig is None:
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
            if kvp[1] != me and itemOnPos is not None and itemOnPos[0] == kvp[1]:
                vals.append(kvp[1])

        if len(vals) == 0:
            return False

        queue = [vals.pop()]
        while len(queue) > 0:
            cur = queue.pop(0)
            near = Shared.CellsNearby(cur.position)
            for cell in near:
                dat = self.Get(cell)
                if dat is not None and dat[0] in vals:
                    vals.remove(dat[0])
                    queue.append(dat[0])

        return len(vals) == 0

    def CheckPlayerPresence(self, pos):
        if self.Get(pos) is not None:
            return [True, True]
        near = Shared.CellsNearby(pos)
        rv = [False, False]
        for cell in near:
            pos = self.Get(cell)
            if pos is not None:
                rv[pos[0].player] = True
                if rv[0] == rv[1]:
                    return rv

        return rv

    def FiguresHash(self, player):
        rv = {}

        for player_id, player_figures in self.figures.items():
            if player_figures.player == player:
                rv[player_id] = player_figures.ToHash()

        return rv

    def AvailableFiguresHash(self, player):
        result = defaultdict(int)

        for figure in self.availFigures[player]:
            result[figure.name] += 1

        return result

    def GetAvailableActions(self, player_num):
        return self.availActions[player_num]

    def GetAvailablePlacements(self, player_num):
        this_player_placements = self.availPlacements[player_num]

        return {
            'figures': [figure.name for figure in this_player_placements[0]],
            'at': this_player_placements[1]
        }
