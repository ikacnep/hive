from ...Utils.Exceptions import *
from .... import Shared


class BeetleFigure:
    canOthers = False

    @staticmethod
    def AvailableTurns(me, field):
        from .FigureTypes import FigureType

        if me.figType != FigureType.Beetle and me.figType != FigureType.Mosquito:
            raise FigureMiss("Wrong figure selected")

        prerv = []
        near = me.CellsNearby()
        filled = []
        isOnTop = len(field.Get(me.position)) > 1
        for cell in near:
            him = field.Get(cell)
            if him is not None:
                inter = Shared.Intersect(near, Shared.CellsNearby(cell))
                if isOnTop:
                    prerv = Shared.Union(prerv, inter)
                else:
                    prerv = Shared.Except(prerv, inter) + Shared.Except(inter, prerv)

                filled.append(cell)

        rv = []
        for cell in prerv:
            if field.Get(cell) is None:
                rv.append(cell)
        rv = rv + filled

        return rv
