import pickle

from .GameState import GameState
from .Utils.Action import Action
from .Utils.Exceptions import *
from ..JsonPYAdaptors.GameActionResult import GameActionResult
from ..JsonPYAdaptors.GameStateData import GameStateData
from ..JsonPYAdaptors.PossibleActionsData import PossibleActionsData

class GameInstance:
    def __init__(self, p0, p1, settings):
        self.game = GameState(settings)
        self.player0 = p0
        self.player1 = p1
        self.lastAction = None
        self.actions = []
        self.noone = [False, False]
        self.settings = settings

    def __eq__(self, other):
        return (
            self.game == other.game and
            self.player0 == other.player0 and
            self.player1 == other.player1 and
            self.noone == other.noone and
            self.settings == other.settings
        )

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(str):
        return pickle.loads(str)

    def __getstate__(self):
        # Выкидываем всю историю действий при сохранении
        banned_attributes = {'actions'}

        return {k: v for k, v in self.__dict__.items() if k not in banned_attributes}

    def __setstate__(self, state):
        for key, value in state.items():
            setattr(self, key, value)

        self.actions = [self.lastAction] if self.lastAction else []

    def GetState(self, addAllActions = False):
        np = self.player1
        if (self.game.turn % 2 == 0):
            np = self.player0
        rv = GameStateData()
        rv.figures = {
            self.player0: self.game.FiguresHash(0),
            self.player1: self.game.FiguresHash(1)
        }
        rv.turn = self.game.turn
        rv.lastAction = self.lastAction
        rv.ended = self.game.gameEnded
        rv.lost = {
            self.player0: self.game.hasLost[0],
            self.player1: self.game.hasLost[1]
        }
        rv.nextPlayer = np

        rv.availableFigures = {
            self.player0: self.game.AvailableFiguresHash(0),
            self.player1: self.game.AvailableFiguresHash(1)
        }

        if addAllActions:
            rv.allActions = self.actions
        return rv

    def GetActions(self):
        np = self.player1
        if (self.game.turn % 2 == 0):
            np = self.player0
        rv = PossibleActionsData()
        rv.placements = {
            self.player0:{
                "figures":self.game.availPlacements[0][0],
                "places":self.game.availPlacements[0][1]
            },
            self.player1:{
                "figures":self.game.availPlacements[1][0],
                "places":self.game.availPlacements[1][1]
            },
        },
        rv.turns = {
            self.player0:self.game.availActions[0],
            self.player1:self.game.availActions[1]
        },
        rv.skips = {
            self.player0:(len(self.game.availPlacements[0]) == 0 and len(self.game.availActions[0]) == 0),
            self.player1: (len(self.game.availPlacements[1]) == 0 and len(self.game.availActions[1]) == 0)
        },
        rv.nextPlayer = np

        return rv

    def GetPlayer(self, id):
        if (id == self.player0):
            return 0
        elif (id == self.player1):
            return 1

        raise PlayerIDException("Player " + repr(id) + " is not participating in this game")


    def Place(self, player, figure, position):
        rv = GameActionResult()

        pid = self.GetPlayer(player)
        id = self.game.Place(pid, figure, position)
        self.noone[0] = False
        self.noone[1] = False
        rv.fid = id
        self.FillPositiveResult(rv)

        action = {
            "action" : Action.Place,
            "player" : player,
            "figure" : figure,
            "position" : position
        }
        self.actions.append(action)
        self.lastAction = action

        return rv

    def Move(self, player, fid, f, t):
        rv = GameActionResult()

        pid = self.GetPlayer(player)
        id = self.game.Move(pid, fid, f, t)
        self.noone[0] = False
        self.noone[1] = False
        rv.fid = id
        self.FillPositiveResult(rv)
        action = {
            "action": Action.Move,
            "player": player,
            "fid": fid,
            "from": f,
            "to": t
        }
        self.actions.append(action)
        self.lastAction = action

        return rv

    def Skip(self, player):
        rv = GameActionResult()

        pid = self.GetPlayer(player)
        self.game.Skip(pid)
        self.noone[0] = False
        self.noone[1] = False
        self.FillPositiveResult(rv)
        action = {
            "action": Action.Skip,
            "player": player,
        }
        self.actions.append(action)
        self.lastAction = action

        return rv

    def Concede(self, player):
        rv = GameActionResult()

        pid = self.GetPlayer(player)
        self.game.gameEnded = True
        self.game.hasLost[pid] = True
        self.noone[0] = False
        self.noone[1] = False
        self.FillPositiveResult(rv)
        action = {
            "action": Action.Concede,
            "player": player,
        }
        self.actions.append(action)
        self.lastAction = action

        return rv

    def ForceEnd(self, player):
        rv = GameActionResult()

        pid = self.GetPlayer(player)
        self.game.gameEnded = True
        self.game.hasLost[pid] = True
        self.noone[0] = False
        self.noone[1] = False
        self.FillPositiveResult(rv)
        action = {
            "action": Action.ForceEnd,
            "player": player,
        }
        self.actions.append(action)
        self.lastAction = action

        return rv

    def Suggest(self, player):
        rv = GameActionResult()

        pid = self.GetPlayer(player)
        self.noone[pid] = True
        if (self.noone[0] == self.noone[1]):
            self.game.gameEnded = True
            self.game.hasLost[0] = True
            self.game.hasLost[1] = True
        self.FillPositiveResult(rv)
        action = {
            "action": Action.Suggest,
            "player": player,
        }
        self.actions.append(action)
        self.lastAction = action

        return rv

    def FillPositiveResult(self, rv):
        rv.result = True
        np = self.player1
        if (self.game.turn % 2 == 0):
            np = self.player0
        rv.nextPlayer = np
        rv.turn = self.game.turn
        rv.ended = self.game.gameEnded
        rv.lost = {
            self.player0: self.game.hasLost[0],
            self.player1: self.game.hasLost[1]
        }

    def ActJS(self, action, addState = False, addActions = True, rv = None):
        if rv == None:
            rv = {"action":action}

        try:
            pid = action["player"]
            act = action["action"]
            tmpRv = None
            if (act == Action.Undefined):
                player = self.GetPlayer(pid)
                raise UnknownAction("Undefined action is not allowed")
            elif (act == Action.Place):
                figure = action["figure"]
                position = action["position"]
                tmpRv = self.Place(pid, figure, position)
            elif (act == Action.Move):
                fid = action["fid"]
                f = action["from"]
                t = action["to"]
                tmpRv = self.Move(pid, fid, f, t)
            elif (act == Action.Skip):
                tmpRv = self.Skip(pid)
            elif (act == Action.Concede):
                tmpRv = self.Concede(pid)
            elif (act == Action.ForceEnd):
                tmpRv = self.ForceEnd(pid)
            elif (act == Action.Suggest):
                tmpRv = self.Suggest(pid)
            else:
                raise UnknownAction("Specified action is unknown")

            if (tmpRv != None):
                tmpRv.FillJson(rv)

            if addState:
                rv["state"] = self.GetState().GetJson()
            if addActions:
                rv["actions"] = self.GetActions().GetJson()
            self.actions.append(action)
            self.lastAction = action

            return rv

        except Exception as ex:
            rv["result"] = False
            rv["reason"] = type(ex)
            rv["message"] = ex.args
            return rv

    def GetSaveData(self):
        rv = {
            "player0" : self.player0,
            "player1" : self.player1,
            "settings": self.settings.parameters,
            "actions" : self.actions,
            "lastState": self.GetState(addAllActions=False).GetJson()
        }
        return rv
