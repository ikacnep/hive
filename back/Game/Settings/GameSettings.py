from Game.Settings.Figures.FigureTypes import FigureType

class GameSettings:
    def __init__(self, figures, limitations = []):
        self.figures = figures
        self.limitations = limitations

    @staticmethod
    def GetSettings(mosquito=False, ladybug=False, pillbug=False, tourney=False):
        figures = [FigureType.Queen] + [FigureType.Spider] * 2 + [FigureType.Beetle] * 2 + [FigureType.Grasshopper] * 3 + [FigureType.Ant] * 3
        if mosquito:
            figures += [FigureType.Mosquito]
        if ladybug:
            figures += [FigureType.Ladybug]
        if pillbug:
            figures += [FigureType.Pillbug]

        limitations = [GameSettings.DefaultLimit]
        if (tourney):
            limitations += [GameSettings.TourneyLimit]

        return GameSettings([figures, figures.copy()], limitations)

    @staticmethod
    def TourneyLimit(field, player, figure):
        if (field.turn < 2 and figure == FigureType.Queen):
            return False

        return  True

    @staticmethod
    def DefaultLimit(field, player, figure):
        if (field.turn >= 5 and field.queens[player] == None and figure != FigureType.Queen):
            return False

        return  True