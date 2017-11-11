#TODO: requires more tests

from Game.GameState import GameState
from Game.Utils.Action import Action
from Game.Utils.Exceptions import *

class GameInstance:
    def __init__(self, p0, p1, settings):
        self.game = GameState(settings)
        self.player0 = p0
        self.player1 = p1
        self.lastAction = None
        self.actions = []
        self.noone = [False, False]
        self.settings = settings

    def GetState(self, addAllActions = False):
        np = self.player1
        if (self.game.turn % 2 == 0):
            np = self.player0
        rv = {
            "figures":{
                    self.player0:self.game.FiguresHash(0),
                    self.player1:self.game.FiguresHash(1)
                },
            "turn":self.game.turn,
            "lastAction":self.lastAction,
            "ended":self.game.gameEnded,
            "lost":{
                self.player0:self.game.hasLost[0],
                self.player1:self.game.hasLost[1]
            },
            "nextPlayer":np
        }
        if addAllActions:
            rv["allActions"] = self.actions
        return rv

    def GetActions(self):
        np = self.player1
        if (self.game.turn % 2 == 0):
            np = self.player0
        return {"placements":{
                    self.player0:{
                        "figures":self.game.availPlacements[0][0],
                        "places":self.game.availPlacements[0][1]
                    },
                    self.player1:{
                        "figures":self.game.availPlacements[1][0],
                        "places":self.game.availPlacements[1][1]
                    },
                },
                "turns":{
                    self.player0:self.game.availActions[0],
                    self.player1:self.game.availActions[1]
                },
                "skips":{
                    self.player0:(len(self.game.availPlacements[0]) == 0 and len(self.game.availActions[0]) == 0),
                    self.player1: (len(self.game.availPlacements[1]) == 0 and len(self.game.availActions[1]) == 0)
                },
                "nextPlayer":np}

    def Act(self, action, addState = False, addActions = True):
        rv = {"action":action}

        try:
            player = action["player"]
            pid = -1
            if (player == self.player0):
                pid = 0
            elif (player == self.player1):
                pid = 1
            else:
                raise PlayerIDException("Player " + repr(player) + " is not participating in this game")

            act = action["action"]
            if (act == Action.Undefined):
                raise UnknownAction("Undefined action is not allowed")
            elif (act == Action.Place):
                figure = action["figure"]
                position = action["position"]
                id = self.game.Place(pid, figure, position)
                rv["fid"] = id
            elif (act == Action.Move):
                fid = action["fid"]
                f = action["from"]
                t = action["to"]
                id = self.game.Move(pid, fid, f, t)
                rv["fid"] = id
            elif (act == Action.Skip):
                self.game.Skip(pid)
            elif (act == Action.Concede):
                self.game.gameEnded = True
                self.game.hasLost[pid] = True
            elif (act == Action.ForceEnd):
                self.game.gameEnded = True
                self.game.hasLost[pid] = True
            elif (act == Action.Suggest):
                self.noone[pid] = True
                if (self.noone[0] == self.noone[1]):
                    self.game.gameEnded = True
                    self.game.hasLost[0] = True
                    self.game.hasLost[1] = True

            rv["result"] = True
            np = self.player1
            if (self.game.turn % 2 == 0):
                np = self.player0
            rv["nextPlayer"] = np
            rv["turn"] = self.game.turn
            rv["ended"] = self.game.gameEnded
            rv["lost"] = {
                self.player0: self.game.hasLost[0],
                self.player1: self.game.hasLost[1]
            }
            if addState:
                rv["state"] = self.GetState()
            if addActions:
                rv["actions"] = self.GetActions()
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
            "lastState": self.GetState(addAllActions=False)
        }
        return rv