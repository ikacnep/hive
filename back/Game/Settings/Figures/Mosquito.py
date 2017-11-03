from Game.Utils.Exceptions import *
import Shared

class MosquitoFigure:

    @staticmethod
    def AvailableTurns(me, field):
        from Game.Settings.Figures.FigureTypes import FigureType

        if (me.figType != FigureType.Mosquito):
            raise FigureMiss("Wrong figure selected")

        myCell = field.Get(me.position)
        if (len(myCell) > 1):
            return FigureType.Beetle.GetClass().AvailTurns()

        rv = []
        near = me.CellsNearby()
        for cell in near:
            him = field.Get(cell)
            if (him != None):
                hisFig = him[0]
                if (hisFig.figType != FigureType.Mosquito):
                    rv = Shared.Union(rv, hisFig.figClass.AvailableTurns(me, field))

        return rv
