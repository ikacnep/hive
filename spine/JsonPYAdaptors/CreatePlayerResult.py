from .ActionResult import ActionResult


class CreatePlayerResult(ActionResult):
    def __init__(self):
        ActionResult.__init__(self)
        self.player = None

    def FillJson(self, rv):
        ActionResult.FillJson(self, rv)
        if self.player is not None:
            rv["player"] = self.player.GetJson()
        else:
            rv["player"] = None
