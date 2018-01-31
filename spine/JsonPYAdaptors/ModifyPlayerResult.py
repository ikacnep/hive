from .ActionResult import ActionResult


class ModifyPlayerResult(ActionResult):
    def __init__(self):
        ActionResult.__init__(self)
        self.player = None

    def FillJson(self, rv):
        ActionResult.FillJson(self, rv)
        rv["player"] = self.player.GetJson()
