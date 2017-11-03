from Game.Settings.Figures.FigureTypes import FigureType

class Action:
    player = 0
    figType = FigureType.Undefined
    figPos = None
    start = None
    end = None

    def __init__(self, action = None):
        if action != None:
            self.player = action[0]
            self.figType = action[1]
            self.figPos = action[2]
            self.start = action[3]
            self.end = action[4]



