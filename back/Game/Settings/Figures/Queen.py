from Game.Utils.Exceptions import *
import Shared

class QueenFigure:
    canOthers = False

    @staticmethod
    def AvailableTurns(me, field):
        from Game.Settings.Figures.FigureTypes import FigureType

        if (me.figType != FigureType.Queen and me.figType != FigureType.Mosquito):
            raise FigureMiss("Wrong figure selected")

        prerv = []
        near = me.CellsNearby()
        for cell in near:
            him = field.Get(cell)
            if (him != None):
                inter = Shared.Intersect(near, Shared.CellsNearby(cell))
                prerv = Shared.Except(prerv, inter) + Shared.Except(inter, prerv)

        rv = []
        for cell in prerv:
            if (field.Get(cell) == None):
                rv.append(cell)

        return rv
