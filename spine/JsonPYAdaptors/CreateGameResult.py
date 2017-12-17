from .ActionResult import ActionResult

class CreateGameResult (ActionResult):
    def __init__(self):
        ActionResult.__init__(self)
        self.gid = None
        self.player1 = None
        self.player2 = None

    def FillJson(self, rv):
        ActionResult.FillJson(self, rv)
        rv["gid"] = self.gid
        rv["player1"] = self.player1
        rv["player2"] = self.player2