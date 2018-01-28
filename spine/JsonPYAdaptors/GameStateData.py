class GameStateData:
    def __init__(self):
        self.figures = None
        self.turn = None
        self.lastAction = None
        self.ended = None
        self.lost = None
        self.nextPlayer = -1
        self.allActions = None
        self.availableFigures = None

    def GetJson(self):
        return {
            "figures" : self.figures,
            "turn" : self.turn,
            "last_action" : self.lastAction,
            "ended" : self.ended,
            "lost" : self.lost,
            "next_player" : self.nextPlayer,
            "all_actions" : self.allActions,
            "available_figures": self.availableFigures,
        }

