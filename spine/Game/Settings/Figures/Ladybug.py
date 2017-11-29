from ...Utils.Exceptions import *
from .... import Shared

class LadybugFigure:
    canOthers = False

    @staticmethod
    def AvailableTurns(me, field):
        from .FigureTypes import FigureType

        if (me.figType != FigureType.Ladybug and me.figType != FigureType.Mosquito):
            raise FigureMiss("Wrong figure selected")

        nextQueue = LadybugFigure.AvailTurns(me, me.position, True, field)
        rv = []
        i = 2
        while (i > 0 and len(nextQueue) > 0):
            i -= 1
            queue = nextQueue
            nextQueue = []
            while (len(queue) > 0):
                cur = queue.pop(0)
                step = LadybugFigure.AvailTurns(me, cur, i != 0, field)
                nextQueue = Shared.Union(nextQueue, step)
            if (i == 0):
                rv = nextQueue


        return rv


    @staticmethod
    def AvailTurns(me, pos, toTop, field):
        rv = []
        near = Shared.CellsNearby(pos)

        for cell in near:
            him = field.Get(cell)
            if (him != None and toTop and him[0] != me) or (him == None and not toTop):
                rv = Shared.Union(rv, [cell])

        return rv
