from Game.Utils.Exceptions import *
import Shared

class SpiderFigure:

    @staticmethod
    def AvailableTurns(me, field):
        from Game.Settings.Figures.FigureTypes import FigureType

        if (me.figType != FigureType.Spider and me.figType != FigureType.Mosquito):
            raise FigureMiss("Wrong figure selected")

        nextQueue = SpiderFigure.AvailTurns(me, ([], me.position), field)
        prerv = []
        i = 2
        while (i > 0 and len(nextQueue) > 0):
            queue = nextQueue
            nextQueue = []
            while (len(queue) > 0):
                cur = queue.pop(0)
                step = SpiderFigure.AvailTurns(me, cur, field)
                nextQueue = Shared.Union(nextQueue, step)
            i -= 1
            if (i == 0):
                prerv = nextQueue


        rv = []
        for cell in prerv:
            if (not Shared.ReallyEqual(cell, me.position)):
                rv = Shared.Union(rv, [cell[1]])

        return rv


    @staticmethod
    def AvailTurns(me, pos, field):
        prerv = []
        near = Shared.CellsNearby(pos[1])

        for cell in near:
            him = field.Get(cell)
            if (him != None and him[0] != me):
                inter = Shared.Intersect(near, Shared.CellsNearby(cell))
                prerv = Shared.Except(prerv, inter) + Shared.Except(inter, prerv)

        rv = []
        for cell in prerv:
            if (field.Get(cell) == None and not Shared.ReallyEqual(cell, pos[0])):
                rv.append((pos[1], cell))

        return rv
