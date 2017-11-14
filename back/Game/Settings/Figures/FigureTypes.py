from enum import IntEnum
from Game.Settings.Figure import *
from Game.Settings.Figures.Queen import *
from Game.Settings.Figures.Spider import *
from Game.Settings.Figures.Grasshopper import *
from Game.Settings.Figures.Ant import *
from Game.Settings.Figures.Beetle import *
from Game.Settings.Figures.Mosquito import *
from Game.Settings.Figures.Ladybug import *
from Game.Settings.Figures.Pillbug import *

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