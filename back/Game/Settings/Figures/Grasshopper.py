from Game.Utils.Exceptions import *
import Shared

class GrasshopperFigure:

    @staticmethod
    def AvailableTurns(me, field):
        from Game.Settings.Figures.FigureTypes import FigureType

        if (me.figType != FigureType.Grasshopper and me.figType != FigureType.Mosquito):
            raise FigureMiss("Wrong figure selected")

        rv = []
        near = me.CellsNearby()
        queue = []
        for cell in near:
            if (field.Get(cell) != None):
                queue.append((me.position, cell))

        while (len(queue) > 0):
            cur = queue.pop(0)
            mov = GrasshopperFigure.NextLinePos(cur[0], cur[1])
            if (field.Get(mov) != None):
                queue.append((cur[1], mov))
            else:
                rv.append(mov)

        return rv

    @staticmethod
    def NextLinePos(pos, next):
        return (next[0] * 2 - pos[0], next[1] * 2 - pos[1])

