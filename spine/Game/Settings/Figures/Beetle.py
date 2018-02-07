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
        filled = set()
        near = me.CellsNearby()
        isOnTop = len(field.Get(me.position)) > 1

        for cell in near:
            him = field.Get(cell)
            if him is not None:
                inter = Shared.Intersect(near, Shared.CellsNearby(cell))
                if isOnTop:
                    prerv = Shared.Union(prerv, inter)
                else:
                    prerv = Shared.Except(prerv, inter) + Shared.Except(inter, prerv)

                filled.add(cell)
            else:
                if isOnTop:
                    inter = Shared.Intersect(near, Shared.CellsNearby(cell))

                    for closing_cell in inter:
                        in_closing_cell = field.Get(closing_cell)

                        if in_closing_cell is None or in_closing_cell[0].layer < me.layer:
                            prerv.append(cell)
                            break

        rv = filled

        for cell in prerv:
            if cell not in rv and field.Get(cell) is None:
                rv.add(cell)

        return list(rv)
