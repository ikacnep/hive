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
        self.telegramId = None

    def GetJson(self):
        rv = {
            "name": self.name,
            "creationDate": self.creationDate,
            "lastGame": self.lastGame,
            "token": self.token,
            "rating": self.rating,
            "premium": self.premium,
            "id": self.id,
            "telegramId": self.telegramId,
        }

        return rv


class GetPlayerResult(ActionResult):
    def __init__(self):
        ActionResult.__init__(self)
        self.player = None

    def FillJson(self, rv):
        ActionResult.FillJson(self, rv)
        rv["player"] = self.player.GetJson()
