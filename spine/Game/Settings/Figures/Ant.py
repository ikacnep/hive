from ...Utils.Exceptions import *
from .... import Shared

class AntFigure:
    canOthers = False

    @staticmethod
    def AvailableTurns(me, field):
        from .FigureTypes import FigureType

        if (me.figType != FigureType.Ant and me.figType != FigureType.Mosquito):
            raise FigureMiss("Wrong figure selected")

        queue = AntFigure.AvailTurns(me, me.position, field)
        rv = []
        while (len(queue) > 0):
            cur = queue.pop(0)
            rv.append(cur)
            step = AntFigure.AvailTurns(me, cur, field)
            step = Shared.Except(step, rv + queue)
            queue = queue + step

        return rv


    @staticmethod
    def AvailTurns(me, pos, field):
        prerv = []
        near = Shared.CellsNearby(pos)

        for cell in near:
            him = field.Get(cell)
            if (him != None and him[0] != me):
                inter = Shared.Intersect(near, Shared.CellsNearby(cell))
                prerv = Shared.Except(prerv, inter) + Shared.Except(inter, prerv)

        rv = []
        for cell in prerv:
            if (field.Get(cell) == None):
                rv.append(cell)

        return rv
