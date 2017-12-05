from .Database.Database import *
from .Game.Utils.Exceptions import *
from .Game.GameInstance import GameInstance
from .Game.Settings.GameSettings import GameSettings
from .Game.Utils.Action import Action

import random
import zlib
import json
import uuid


class GamesManipulator:
    players = None
    games = None
    archive = None
    runningGames = {}

    def __init__(self, playerType=Player, gameType=Game, archType=GameArchieved):
        self.players = playerType
        if not self.players.table_exists():
            self.players.create_table()

        self.games = gameType
        if not self.games.table_exists():
            self.games.create_table()

        self.archive = archType
        if not self.archive.table_exists():
            self.archive.create_table()

        self.runningGames = {}

    def CreateGame(self, player1, player2, mosquito, ladybug, pillbug, tourney, rv):
        try:
            p1 = self.players.get(self.players.id == player1)
            p2 = self.players.get(self.players.id == player2)
        except Exception as ex:
            raise PlayerNotFoundException("Player not found.", ex.args)

        game = self.games.create(player1=p1, player2=p2)
        actualGame = GameInstance(player1, player2,
                                  GameSettings.GetSettings(mosquito=mosquito, ladybug=ladybug, pillbug=pillbug,
                                                           tourney=tourney))
        self.runningGames[game.id] = actualGame

        rv["gid"] = game.id
        rv["player1"] = player1
        rv["player2"] = player2

        return actualGame

    def Act_CreateGame(self, action, rv):
        p1 = action["player1"]
        p2 = action["player2"]
        turn = None
        if "turn" in action:
            turn = action["turn"]
            if turn != p1 and turn != p2:
                turn = None

        if turn is None:
            if bool(random.getrandbits(0)):
                turn = p2

        if turn == p2:
            tmp = p2
            p2 = p1
            p1 = tmp

        mosquito = False
        if "mosquito" in action:
            mosquito = action["mosquito"]

        ladybug = False
        if "ladybug" in action:
            ladybug = action["ladybug"]

        pillbug = False
        if "pillbug" in action:
            pillbug = action["pillbug"]

        tourney = False
        if "tourney" in action:
            tourney = action["tourney"]

        return self.CreateGame(p1, p2, mosquito, ladybug, pillbug, tourney, rv)

    def Act_GetGames(self, action, rv):
        try:
            includeArch = False
            if "archived" in action:
                includeArch = action["archived"]

            rv["games"] = []
            if "gid" in action:
                gid = action["gid"]
                if gid in self.runningGames:
                    theGame = self.games.get(self.games.id == gid)
                    rv["games"].append(Game.ToHash(theGame))
                elif includeArch:
                    theGame = self.archive.get(self.archive.gameid == gid)
                    rv["games"].append(GameArchieved.ToHash(theGame))
            else:
                if "players" in action:
                    players = action["players"]
                    try:
                        p1 = self.players.get(self.players.id == players[0])
                        p2 = None
                        if len(players) > 1:
                            p2 = self.players.get(self.players.id == players[1])
                    except Exception as ex:
                        raise PlayerNotFoundException("Player with specified ID not found", ex.args)

                    if p2 is None:
                        try:
                            for theGame in self.games.select().where(self.games.player1 == p1 or self.games.player2 == p1):
                                rv["games"].append(Game.ToHash(theGame))
                        except Exception as ex:
                            pass
                        if includeArch:
                            try:
                                for theGame in self.archive.select().where(
                                                        self.archive.player1 == p1 or self.archive.player2 == p1):
                                    rv["games"].append(GameArchieved.ToHash(theGame))
                            except:
                                pass
                    else:
                        try:
                            for theGame in self.games.select().where((
                                                         self.games.player1 == p1 and self.games.player2 == p2) or
                                                         (self.games.player1 == p2 and self.games.player2 == p1)):
                                rv["games"].append(Game.ToHash(theGame))
                        except:
                            pass

                        if includeArch:
                            try:
                                for theGame in self.archive.select().where(
                                                (
                                                        self.archive.player1 == p1 and self.archive.player2 == p2) or
                                                (
                                                        self.archive.player1 == p2 and self.archive.player2 == p1)):
                                    rv["games"].append(GameArchieved.ToHash(theGame))
                            except:
                                pass
                else:
                    rv["games"] = []
                    for theGame in self.games.select():
                        rv["games"].append(Game.ToHash(theGame))
                    if includeArch:
                        for theGame in self.archive.select():
                            rv["games"].append(GameArchieved.ToHash(theGame))

            if len(rv["games"]) == 0:
                raise GameNotFoundException("Game with specified parameters not found")
        except PlayerNotFoundException as ex:
            raise ex
        except Exception as ex:
            raise GameNotFoundException("Game with specified parameters not found", ex.args)

    def Act_GetPlayer(self, action, rv):
        player = None
        try:
            if "token" in action:
                token = action["token"]
                player = self.players.get(self.players.token == token)
            elif "telegramId" in action:
                telegramId = action["telegramId"]
                player = self.players.get(self.players.telegramId == telegramId)
            elif "login" in action and "password" in action:
                login = action["login"]
                password = action["password"]
                player = self.players.get(
                    self.players.login == login and self.players.password == password)
        except Exception as ex:
            raise PlayerNotFoundException("Player with specified parameters not found", ex.args)

        if player is None:
            raise PlayerNotFoundException("Necessary parameters not specified")

        if "refreshToken" in action and action["refreshToken"]:
            player.token = str(self.GetToken())
            player.save()

        rv["player"] = Player.ToHash(player)

        return player

    def Act_CreatePlayer(self, action, rv):
        name = None
        if "name" in action:
            name = action["name"]
        login = None
        if "login" in action:
            p = None
            login = action["login"]
            try:
                p = self.players.get(self.players.login == login)
            except:
                pass
            if p is not None:
                raise PlayerCreationException("Login is already in use")
        password = None
        if "password" in action:
            password = action["password"]
        telegramId = None
        if "telegramId" in action:
            telegramId = action["telegramId"]
            p = None
            try:
                p = self.players.get(self.players.telegramId == telegramId)
            except Exception as ex:
                pass

            if p is not None:
                raise PlayerCreationException("This telegramid is already in use")
        premium = False
        if "premium" in action:
            premium = action["premium"]

        if login is None and telegramId is None:
            raise PlayerCreationException("Cannot create player without login and telegram id. No way for him to join the club")

        p = self.players.create(
            name=name,
            login=login,
            password=password,
            telegramId=telegramId,
            premium=premium,
            token=str(self.GetToken())
        )
        rv["player"] = Player.ToHash(p)

    def Act_DoAction(self, action, rv):
        gid = action["gid"]
        if gid not in self.runningGames:
            raise GameNotFoundException("No such ID in running games")
        gameInst = self.runningGames[gid]
        gameInst.Act(action, False, False, rv)
        rv["gid"] = gid
        if rv["ended"]:
            self.runningGames.pop(gid)
            try:
                p1 = self.players.get(self.players.id == gameInst.player0)
                p2 = self.players.get(self.players.id == gameInst.player1)
            except Exception as ex:
                raise PlayerNotFoundException("Player not found.", ex.args)

            try:
                game = self.games.get(self.games.id == gid)
            except Exception as ex:
                raise GameNotFoundException("No such ID in database.", ex.args)

            res = 0
            if rv["lost"][p1.id]:
                res += 1
            if rv["lost"][p2.id]:
                res -= 1
            ratingChange = self.GetEloRate(p1.rating, p2.rating, res)

            self.archive.create(
                player1=p1,
                player2=p2,
                gameid=gid,
                length=gameInst.game.turn,
                result1=ratingChange[0],
                result2=ratingChange[1],
                start=game.start,
                end=datetime.datetime.now(),
                log=zlib.compress(json.dumps(gameInst.actions).encode("utf-8"))
            )
            game.delete_instance()
            p1.rating += ratingChange[0]
            p2.rating += ratingChange[1]
            p1.lastGame = datetime.datetime.now()
            p2.lastGame = datetime.datetime.now()
            p1.save()
            p2.save()
            rv["rateChange"] = {
                p1.id: ratingChange[0],
                p2.id: ratingChange[1]
            }

        return gameInst

    def Act_ModifyPlayer(self, action, rv):
        tmp = {}
        p = self.Act_GetPlayer(action, tmp)

        newVals = action["newValues"]
        if "name" in newVals:
            p.name = newVals["name"]
        if "login" in newVals:
            log = newVals["login"]
            if log != p.login:
                tmpP = None
                try:
                    tmpP = self.players.get(self.players.login == log)
                except:
                    pass
                if tmpP is not None:
                    raise PlayerModificationException("login is already in use")
                p.login = log
        if "password" in newVals:
            p.password = newVals["password"]
        if "telegramId" in newVals:
            p.telegramId = newVals["telegramId"]
        if "premium" in newVals:
            p.premium = newVals["premium"]

        p.save()
        rv["player"] = Player.ToHash(p)

    def Act(self, action):
        rv = {"action": action}
        try:
            act = action["action"]
            game = None
            if act == Action.CreateGame:
                game = self.Act_CreateGame(action, rv)
            elif act == Action.GetGames:
                self.Act_GetGames(action, rv)
            elif act == Action.GetPlayer:
                self.Act_GetPlayer(action, rv)
            elif act == Action.CreatePlayer:
                self.Act_CreatePlayer(action, rv)
            elif act == Action.ModifyPlayer:
                self.Act_ModifyPlayer(action, rv)
            elif act == Action.CreatePlayer:
                try:
                    self.Act_GetPlayer(action, rv)
                except:
                    self.Act_CreatePlayer(action, rv)
            elif act in (Action.Move, Action.Place, Action.ForceEnd, Action.Suggest, Action.Concede, Action.Skip):
                game = self.Act_DoAction(action, rv)
            elif act == Action.Undefined:
                raise UnknownAction("Undefined action is not allowed")
            else:
                raise UnknownAction("Unknown action: %s" % act)

            if "addActions" in action and game is not None and action["addActions"]:
                rv["actions"] = game.GetActions()
            if "addState" in action and game is not None and action["addState"]:
                addAllActions = False
                if "addAllActions" in action:
                    addAllActions = action["addAllActions"]
                rv["state"] = game.GetState(addAllActions=addAllActions)

            rv["result"] = True
            return rv
        except Exception as ex:
            rv["result"] = False
            rv["reason"] = type(ex)
            rv["message"] = ex.args
            return rv

    @staticmethod
    def GetEloRate(rate1, rate2, result):
        q1 = pow(10, rate1/400)
        q2 = pow(10, rate2/400)
        e1 = q1 / (q1 + q2)
        e2 = q2 / (q1 + q2)
        s1 = 0.5
        s2 = 0.5
        if result == -1:
            s1 = 1
            s2 = 0
        elif result == 1:
            s1 = 0
            s2 = 1
        rv = [0, 0]
        k1 = 32
        k2 = 32
        if rate1 > 1900:
            k1 = 16
        if rate2 > 1900:
            k2 = 16
        rv[0] = k1 * (s1 - e1)
        rv[1] = k2 * (s2 - e2)

        return rv

    def GetToken(self):
        while True:
            newToken = uuid.uuid4()
            try:
                p = self.players.get(self.players.token == newToken)

                if not p:
                    return newToken
            except:
                return newToken
