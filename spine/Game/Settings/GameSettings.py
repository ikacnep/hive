from .Figures.FigureTypes import FigureType


class GameSettings:
    def __init__(self, figures, limitations, parameters):
        self.figures = figures
        self.limitations = limitations
        self.parameters = parameters

    def __eq__(self, other):
        return (
                self.figures == other.figures and
                self.limitations == other.limitations and
                self.parameters == other.parameters
        )

    @staticmethod
    def GetSettings(mosquito=False, ladybug=False, pillbug=False, tourney=False):
        figures = [FigureType.Queen] + [FigureType.Spider] * 2 + [FigureType.Beetle] * 2 + \
                [FigureType.Grasshopper] * 3 + [FigureType.Ant] * 3

        if mosquito:
            figures += [FigureType.Mosquito]

        if ladybug:
            figures += [FigureType.Ladybug]

        if pillbug:
            figures += [FigureType.Pillbug]

        limitations = [GameSettings.DefaultLimit]

        if tourney:
            limitations += [GameSettings.TourneyLimit]

        parameters = {
            "mosquito": mosquito,
            "ladybug": ladybug,
            "pillbug": pillbug,
            "tourney": tourney
        }

        return GameSettings([figures, figures.copy()], limitations, parameters)

    @staticmethod
    def TourneyLimit(field, _, figure):
        if field.turn < 2 and figure == FigureType.Queen:
            return False

        return True

    @staticmethod
    def DefaultLimit(field, player, figure):
        if field.turn >= 5 and field.queens[player] is None and figure != FigureType.Queen:
            return False

        return True
