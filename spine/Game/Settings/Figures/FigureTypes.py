from enum import IntEnum
from ..Figure import *
from .Queen import *
from .Spider import *
from .Grasshopper import *
from .Ant import *
from .Beetle import *
from .Mosquito import *
from .Ladybug import *
from .Pillbug import *

class FigureType(IntEnum):
    Undefined = 0
    Queen = 1
    Spider = 2
    Beetle = 3
    Grasshopper = 4
    Ant = 5
    Mosquito = 6
    Ladybug = 7
    Pillbug = 8

    def GetFigure(self, player, pos):
        c = self.GetClass()
        if (c == None):
            return None

        return Figure(self, c, player, pos)

    def GetClass(self):
        if (self == FigureType.Queen):
            return QueenFigure
        if (self == FigureType.Spider):
            return SpiderFigure
        if (self == FigureType.Beetle):
            return BeetleFigure
        if (self == FigureType.Grasshopper):
            return GrasshopperFigure
        if (self == FigureType.Ant):
            return AntFigure
        if (self == FigureType.Mosquito):
            return MosquitoFigure
        if (self == FigureType.Ladybug):
            return LadybugFigure
        if (self == FigureType.Pillbug):
            return PillbugFigure
        return None

    def Name(self):
        return self.name.lower()
