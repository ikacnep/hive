import enum
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
    def deserialize(string):
        return pickle.loads(string)

    def __getstate__(self):
        # Выкидываем всю историю действий при сохранении
        banned_attributes = {'actions'}

        return {k: v for k, v in self.__dict__.items() if k not in banned_attributes}

    def __setstate__(self, state):
        for key, value in state.items():
            setattr(self, key, value)

        self.actions = [self.lastAction] if self.lastAction else []

    def GetState(self, addAllActions=False):
        def categorize_by_player(method):
            return {
                self.player0: method(0),
                self.player1: method(1)
            }

        np = self.NextPlayer()
        rv = GameStateData()

        rv.figures = categorize_by_player(self.game.FiguresHash)

        rv.turn = self.game.turn

        if self.lastAction:
            rv.lastAction = {k: (v.name if isinstance(v, enum.Enum) else v) for k, v in self.lastAction.items()}

        rv.ended = self.game.gameEnded
        rv.lost = {
            self.player0: self.game.hasLost[0],
            self.player1: self.game.hasLost[1]
        }
        rv.nextPlayer = np

        rv.availableFigures = categorize_by_player(self.game.AvailableFiguresHash)
        rv.availableActions = categorize_by_player(self.game.GetAvailableActions)
        rv.availablePlacements = categorize_by_player(self.game.GetAvailablePlacements)

        if addAllActions:
            rv.allActions = self.actions
        return rv

    def GetActions(self):
        np = self.NextPlayer()
        rv = PossibleActionsData()
        rv.placements = {
            self.player0: {
                "figures": self.game.availPlacements[0][0],
                "places": self.game.availPlacements[0][1]
            },
            self.player1: {
                "figures": self.game.availPlacements[1][0],
                "places": self.game.availPlacements[1][1]
            },
        },
        rv.turns = {
            self.player0: self.game.availActions[0],
            self.player1: self.game.availActions[1]
        },
        rv.skips = {
            self.player0: (len(self.game.availPlacements[0]) == 0 and len(self.game.availActions[0]) == 0),
            self.player1: (len(self.game.availPlacements[1]) == 0 and len(self.game.availActions[1]) == 0)
        },
        rv.nextPlayer = np

        return rv

    def NextPlayer(self):
        return self.player0 if self.game.turn % 2 == 0 else self.player1

    def GetPlayer(self, player_id):
        if player_id == self.player0:
            return 0

        elif player_id == self.player1:
            return 1

        raise PlayerIDException("Player " + repr(player_id) + " is not participating in this game")

    def Place(self, player, figure, position):
        rv = GameActionResult()

        pid = self.GetPlayer(player)
        placed_fid = self.game.Place(pid, figure, position)
        self.noone[0] = False
        self.noone[1] = False
        rv.fid = placed_fid
        self.FillPositiveResult(rv)

        action = {
            "action": Action.Place,
            "player": player,
            "figure": figure,
            "position": position,
            "fid": placed_fid,
        }
        self.actions.append(action)
        self.lastAction = action

        return rv

    def Move(self, player, fid, f, t):
        rv = GameActionResult()

        pid = self.GetPlayer(player)
        moved_fid = self.game.Move(pid, fid, f, t)
        self.noone[0] = False
        self.noone[1] = False
        rv.fid = moved_fid
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
        if self.noone[0] == self.noone[1]:
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

    def CloseGame(self):
        rv = GameActionResult()

        rv.result = True

        rv.turn = self.game.turn
        rv.ended = self.game.gameEnded
        rv.lost = {
            self.player0: self.game.hasLost[0],
            self.player1: self.game.hasLost[1]
        }

        return rv

    def FillPositiveResult(self, rv):
        rv.result = True
        np = self.NextPlayer()
        rv.nextPlayer = np
        rv.turn = self.game.turn
        rv.ended = self.game.gameEnded
        rv.lost = {
            self.player0: self.game.hasLost[0],
            self.player1: self.game.hasLost[1]
        }

    def ActJS(self, action, addState=False, addActions=True, rv=None):
        if rv is None:
            rv = {"action": action}

        try:
            pid = action["player"]
            act = action["action"]

            if act == Action.Undefined:
                self.GetPlayer(pid)
                raise UnknownAction("Undefined action is not allowed")
            elif act == Action.Place:
                figure = action["figure"]
                position = action["position"]
                tmpRv = self.Place(pid, figure, position)
            elif act == Action.Move:
                fid = action["fid"]
                f = action["from"]
                t = action["to"]
                tmpRv = self.Move(pid, fid, f, t)
            elif act == Action.Skip:
                tmpRv = self.Skip(pid)
            elif act == Action.Concede:
                tmpRv = self.Concede(pid)
            elif act == Action.ForceEnd:
                tmpRv = self.ForceEnd(pid)
            elif act == Action.Suggest:
                tmpRv = self.Suggest(pid)
            else:
                raise UnknownAction("Specified action is unknown")

            if tmpRv is not None:
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
            "player0": self.player0,
            "player1": self.player1,
            "settings": self.settings.parameters,
            "actions": self.actions,
            "lastState": self.GetState(addAllActions=False).GetJson()
        }
        return rv
