from .ActionResult import ActionResult

class PlayerResult:
    def __init__(self):
        self.name = None
        self.creationDate = None
        self.lastGame = None
        self.token = None
        self.rating = None
        self.premium = None
        self.id = None

    def GetJson(self):
            rv = {}
            rv["name"] = self.name
            rv["creationDate"] = self.creationDate
            rv["lastGame"] = self.lastGame
            rv["token"] = self.token
            rv["rating"] = self.rating
            rv["premium"] = self.premium
            rv["id"] = self.id

            return rv

class GetPlayerResult (ActionResult):
    def __init__(self):
        ActionResult.__init__(self)
        self.player = None

    def FillJson(self, rv):
        ActionResult.FillJson(self, rv)
        rv["player"] = self.player.GetJson()