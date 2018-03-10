from spine.JsonPYAdaptors.ActionResult import ActionResult


class LobbyRoom:
    def __init__(self):
        self.id = None
        self.gid = None  # Идентификатор созданной игры
        self.source = None  # Внешний идентификатор, например, inline_message_id в телеге
        self.name = None
        self.owner = None
        self.guest = None
        self.creationDate = None
        self.expirationDate = None
        self.duration = None
        self.ownerReady = False
        self.guestReady = False
        self.mosquito = False
        self.ladybug = False
        self.pillbug = False
        self.tourney = False

    def GetJson(self):
        rv = {
            "name": self.name,
            "owner": self.owner,
            "guest": self.guest,
            "creationDate": self.creationDate,
            "duration": self.duration,
            "expirationDate": self.expirationDate,
            "ownerReady": self.ownerReady,
            "guestReady": self.guestReady,
            "mosquito": self.mosquito,
            "ladybug": self.ladybug,
            "pillbug": self.pillbug,
            "tourney": self.tourney,
            "id": self.id,
            "gid": self.gid
        }

        return rv

class QuickGame:
    def __init__(self):
        self.id = None
        self.player = None
        self.player2 = None
        self.mosquito = False
        self.ladybug = False
        self.pillbug = False
        self.tourney = False
        self.rating = None
        self.creationDate = None

    def GetJson(self):
        rv = {
            "player": self.player,
            "player2": self.player2,
            "mosquito": self.mosquito,
            "ladybug": self.ladybug,
            "pillbug": self.pillbug,
            "tourney": self.tourney,
            "rating": self.rating,
            "creationDate": self.creationDate,
            "id": self.id
        }

        return rv

class SuccessResult:
    def __init__(self):
        self.success = None

    def GetJson(self):
        rv = {
            "success": self.success
        }

        return rv

class GetLobbyResult(ActionResult):
    def __init__(self):
        ActionResult.__init__(self)
        self.lobbys = None

    def FillJson(self, rv):
        ActionResult.FillJson(self, rv)
        if self.lobbys is not None:
            ls = []
            for l in self.lobbys:
                ls.append(l.GetJson())
            rv["lobbys"] = ls

class GetQuickGameResult(ActionResult):
    def __init__(self):
        ActionResult.__init__(self)
        self.quickGames = None

    def FillJson(self, rv):
        ActionResult.FillJson(self, rv)
        if self.quickGames is not None:
            qgs = []
            for qg in self.quickGames:
                qgs.append(l.GetJson())
            rv["quickGames"] = qgs
