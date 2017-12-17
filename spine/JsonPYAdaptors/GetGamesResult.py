from .ActionResult import ActionResult

class GameResult:
    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.gid = None
        self.start = None
        self.hasEnded = False

    def GetJson(self):
        rv = {}
        rv["player1"] = self.player1
        rv["player2"] = self.player2
        rv["gid"] = self.gid
        rv["start"] = self.start
        rv["hasEnded"] = self.hasEnded
        return rv

class ArchGameResult(GameResult):
    def __init__(self):
        GameResult.__init__(self)
        self.hasEnded = True
        self.length = None
        self.result1 = None
        self.result2 = None
        self.end = None

    def GetJson(self):
        rv = GameResult.GetJson(self)
        rv["length"] = self.length
        rv["result1"] = self.result1
        rv["result2"] = self.result2
        rv["end"] = self.end
        return rv

class GetGamesResult (ActionResult):
    def __init__(self):
        ActionResult.__init__(self)
        self.games = None

    def FillJson(self, rv):
        ActionResult.FillJson(self, rv)
        if (self.games != None):
            gs = []
            for g in self.games:
                gs.append(g.GetJson())
            rv["games"] = gs