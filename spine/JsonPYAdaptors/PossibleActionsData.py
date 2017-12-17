class PossibleActionsData:
    def __init__(self):
        self.placements = None
        self.turns = None
        self.skips = None
        self.nextPlayer = None

    def GetJson(self):
        return {
            "placements" : self.placements,
            "turns" : self.turns,
            "skips" : self.skips,
            "nextPlayer" : self.nextPlayer
        }

