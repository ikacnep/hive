from ...Utils.Exceptions import *
from .... import Shared


class MosquitoFigure:
    canOthers = True

    @staticmethod
    def AvailableTurns(me, field):
        from .FigureTypes import FigureType

        if me.figType != FigureType.Mosquito:
            raise FigureMiss("Wrong figure selected")

        myCell = field.Get(me.position)
        if len(myCell) > 1:
            return FigureType.Beetle.GetClass().AvailableTurns(me, field)

        rv = []
        near = me.CellsNearby()
        for cell in near:
            him = field.Get(cell)
            if him is not None:
                hisFig = him[0]
                if hisFig.figType != FigureType.Mosquito:
                    rv = Shared.Union(rv, hisFig.figClass.AvailableTurns(me, field))

        return rv

    @staticmethod
    def AvailableOthers(me, field):
        from .FigureTypes import FigureType

        if me.figType != FigureType.Mosquito:
            raise FigureMiss("Wrong figure selected")

        myCell = field.Get(me.position)
        if len(myCell) > 1:
            return []

        rv = []
        near = me.CellsNearby()
        for cell in near:
            him = field.Get(cell)
            if him is not None:
                hisFig = him[0]
                if hisFig.figType != FigureType.Mosquito and hisFig.figClass.canOthers:
                    rv = Shared.Union(rv, hisFig.figClass.AvailableOthers(me, field))

        return rv
