class GameStateData:
    def __init__(self):
        self.figures = None
        self.turn = None
        self.lastAction = None
        self.ended = None
        self.lost = None
        self.nextPlayer = -1
        self.allActions = None

    def GetJson(self):
        return {
            "figures" : self.figures,
            "turn" : self.turn,
            "lastAction" : self.lastAction,
            "ended" : self.ended,
            "lost" : self.lost,
            "nextPlayer" : self.nextPlayer,
            "allActions" : self.allActions
        }

