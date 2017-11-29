from ...Utils.Exceptions import *
from .... import Shared

class PillbugFigure:
    canOthers = True

    @staticmethod
    def AvailableTurns(me, field):
        from .FigureTypes import FigureType

        if (me.figType != FigureType.Pillbug and me.figType != FigureType.Mosquito):
            raise FigureMiss("Wrong figure selected")

        prerv = []
        filled = []
        empty = []
        near = me.CellsNearby()
        for cell in near:
            him = field.Get(cell)
            if (him != None):
                inter = Shared.Intersect(near, Shared.CellsNearby(cell))
                prerv = Shared.Except(prerv, inter) + Shared.Except(inter, prerv)
                if (field.CheckIntegrity(him[0]) and field.lastMoved != him[0]):
                    filled.append(cell)
            else:
                empty.append(cell)

        rv = []
        for cell in prerv:
            if (field.Get(cell) == None):
                rv.append(cell)

        for cell in filled:
            for pos in empty:
                rv.append((cell, pos))

        return rv

    @staticmethod
    def AvailableOthers(me, field):
        from .FigureTypes import FigureType

        if (me.figType != FigureType.Pillbug and me.figType != FigureType.Mosquito):
            raise FigureMiss("Wrong figure selected")

        filled = []
        empty = []
        near = me.CellsNearby()
        for cell in near:
            him = field.Get(cell)
            if (him != None):
                if (field.CheckIntegrity(him[0]) and field.lastMoved != him[0]):
                    filled.append(cell)
            else:
                empty.append(cell)

        rv = []
        for cell in filled:
            for pos in empty:
                rv.append((cell, pos))

        return rv
