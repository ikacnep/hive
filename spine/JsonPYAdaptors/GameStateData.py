class GameStateData:
    figures = None
    turn = None
    lastAction = None
    ended = None
    lost = None
    nextPlayer = -1
    allActions = None
    availableFigures = None
    availableActions = None
    availablePlacements = None

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
            "available_actions": self.availableActions,
            "available_placements": self.availablePlacements,
        }

