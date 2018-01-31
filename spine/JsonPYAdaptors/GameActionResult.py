from .ActionResult import ActionResult


class GameActionResult(ActionResult):
    def __init__(self):
        ActionResult.__init__(self)
        self.gid = None
        self.nextPlayer = None
        self.turn = None
        self.ended = None
        self.lost = None
        self.fid = None
        self.rateChange = None

    def FillJson(self, rv):
        ActionResult.FillJson(self, rv)
        rv["gid"] = self.gid
        rv["nextPlayer"] = self.nextPlayer
        rv["turn"] = self.turn
        rv["ended"] = self.ended
        rv["lost"] = self.lost
        if self.fid is not None:
            rv["fid"] = self.fid
        if self.rateChange is not None:
            rv["rateChange"] = self.rateChange
