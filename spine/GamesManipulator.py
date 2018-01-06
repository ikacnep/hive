from .Database.Database import *
from .Game.Utils.Exceptions import *
from .Game.GameInstance import GameInstance
from .Game.Settings.GameSettings import GameSettings
from .Game.Utils.Action import Action
from .Game.GameState import GameState
from .JsonPYAdaptors.CreateGameResult import CreateGameResult
from .JsonPYAdaptors.GetGamesResult import GetGamesResult
from .JsonPYAdaptors.GetPlayerResult import GetPlayerResult
from .JsonPYAdaptors.CreatePlayerResult import CreatePlayerResult
from .JsonPYAdaptors.ModifyPlayerResult import ModifyPlayerResult
from .JsonPYAdaptors.GameActionResult import GameActionResult

import random
import zlib
import json
import uuid


class GamesManipulator:
    players = None
    games = None
    archive = None
    runningGames = {}

    def __init__(self, playerType=Player, gameType=Game, archType=GameArchieved, gameStateTable=PersistedGameState):
        self.players = playerType
        if not self.players.table_exists():
            self.players.create_table()

        self.games = gameType
        if not self.games.table_exists():
            self.games.create_table()

        self.archive = archType
        if not self.archive.table_exists():
            self.archive.create_table()

        self.game_state_table = gameStateTable
        if not self.game_state_table.table_exists():
            self.game_state_table.create_table()

        self.runningGames = {}
        for game_state in gameStateTable.select():
            self.runningGames[game_state.id] = GameInstance.deserialize(game_state.state)

    def CreateGameInner(self, player1, player2, mosquito, ladybug, pillbug, tourney, rv):
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

        rv.gid = game.id
        rv.player1 = player1
        rv.player2 = player2

        return actualGame

    def CreateGame(self, player1, player2, turn=None, mosquito=False, ladybug=False, pillbug=False, tourney=False, addActions=False, addAllActions=False, addState=False):
        rv = CreateGameResult()

        if turn != player1 and turn != player2:
            turn = None

        if turn is None:
            if bool(random.getrandbits(1)):
                turn = player2

        if turn == player2:
            tmp = player2
            player2 = player1
            player1 = tmp

        game = self.CreateGameInner(player1, player2, mosquito, ladybug, pillbug, tourney, rv)
        self._persist_game(rv.gid)

        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)

        return rv

    def GetGames(self, includeArch=False, gid=None, players=None):
        rv = GetGamesResult()
        try:
            rv.games = []
            if gid != None:
                if gid in self.runningGames:
                    theGame = self.games.get(self.games.id == gid)
                    rv.games.append(Game.ToClass(theGame))
                elif includeArch:
                    theGame = self.archive.get(self.archive.gameid == gid)
                    rv.games.append(GameArchieved.ToClass(theGame))
            else:
                if players != None:
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
                                rv.games.append(Game.ToClass(theGame))
                        except Exception as ex:
                            pass
                        if includeArch:
                            try:
                                for theGame in self.archive.select().where(
                                                        self.archive.player1 == p1 or self.archive.player2 == p1):
                                    rv.games.append(GameArchieved.ToClass(theGame))
                            except:
                                pass
                    else:
                        try:
                            for theGame in self.games.select().where((
                                                         self.games.player1 == p1 and self.games.player2 == p2) or
                                                         (self.games.player1 == p2 and self.games.player2 == p1)):
                                rv.games.append(Game.ToClass(theGame))
                        except:
                            pass

                        if includeArch:
                            try:
                                for theGame in self.archive.select().where(
                                                (
                                                        self.archive.player1 == p1 and self.archive.player2 == p2) or
                                                (
                                                        self.archive.player1 == p2 and self.archive.player2 == p1)):
                                    rv.games.append(GameArchieved.ToClass(theGame))
                            except:
                                pass
                else:
                    rv.games = []
                    for theGame in self.games.select():
                        rv.games.append(Game.ToClass(theGame))
                    if includeArch:
                        for theGame in self.archive.select():
                            rv.games.append(GameArchieved.ToClass(theGame))

            if len(rv.games) == 0:
                raise GameNotFoundException("Game with specified parameters not found")
        except Exception as ex:
            rv.result = False
            rv.reason = type(ex)
            rv.message = ex.args

        return rv


    def GetPlayerInner(self, token=None, telegramId=None, login=None, password=None, refreshToken=False):
        player = None
        try:
            if token != None:
                player = self.players.get(self.players.token == token)
            elif telegramId != None:
                player = self.players.get(self.players.telegramId == telegramId)
            elif login != None and password != None:
                player = self.players.get(
                    self.players.login == login and self.players.password == password)
        except Exception as ex:
            raise PlayerNotFoundException("Player with specified parameters not found", ex.args)

        if player is None:
            raise PlayerNotFoundException("Necessary parameters not specified")

        if refreshToken:
            player.token = str(self.GetToken())
            player.save()

        return player

    def GetPlayer(self, token=None, telegramId=None, login=None, password=None, refreshToken=False):
        rv = GetPlayerResult()

        try:
            player = self.GetPlayerInner(token, telegramId, login, password, refreshToken)
            rv.player = Player.ToClass(player)

        except Exception as ex:
            rv.result = False
            rv.reason = type(ex)
            rv.message = ex.args

        return rv

    def CreatePlayer(self, name=None, login=None, password=None, telegramId=None, premium=False):
        rv = CreatePlayerResult()

        if login != None:
            p = None
            try:
                p = self.players.get(self.players.login == login)
            except:
                pass
            if p is not None:
                raise PlayerCreationException("Login is already in use")

        if telegramId != None:
            p = None
            try:
                p = self.players.get(self.players.telegramId == telegramId)
            except Exception as ex:
                pass

            if p is not None:
                raise PlayerCreationException("This telegramid is already in use")

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
        rv.player = Player.ToClass(p)

        return rv

    def GetOrCreatePlayer(self, token=None, name=None, login=None, password=None, telegramId=None, premium=False, refreshToken=False):
        rv = self.GetPlayer(token, telegramId, login, password, refreshToken)
        if not rv.result:
            rv = self.CreatePlayer(name, login, password, telegramId, premium)

        return rv

    def ModifyPlayer(self, token=None, telegramId=None, login=None, password=None, refreshToken=False, newName=None, newLogin=None, newPassword=None, newTelegramId=None, newPremium=None):
        rv = ModifyPlayerResult()

        p = self.GetPlayerInner(token, telegramId, login, password, refreshToken)

        if newLogin != None and newLogin != login:
            tmpP = None
            try:
                tmpP = self.players.get(self.players.login == newLogin)
            except:
                pass
            if tmpP is not None:
                raise PlayerModificationException("login is already in use")
            p.login = newLogin

        if newName != None:
            p.name = newName
        if newPassword != None:
            p.password = newPassword
        if newTelegramId != None:
            tmpP = None
            try:
                tmpP = self.players.get(self.players.telegramId == newTelegramId)
            except:
                pass
            if tmpP is not None:
                raise PlayerModificationException("telegram ID is already in use")
            p.telegramId = newTelegramId
        if newPremium != None:
            p.premium = newPremium

        p.save()

        rv.player = Player.ToClass(p)

        return rv

    def GetGameInst(self, gid):
        if gid not in self.runningGames:
            raise GameNotFoundException("No such ID in running games")
        gameInst = self.runningGames[gid]

        return gameInst

    def ProcessEndgame(self, gid, gameInst, rv):
        if rv.ended:
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
            if rv.lost[p1.id]:
                res += 1
            if rv.lost[p2.id]:
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
            rv.rateChange = {
                p1.id: ratingChange[0],
                p2.id: ratingChange[1]
            }

        self._persist_game(gid)

    def Place(self, gid, player, figure, position, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.Place(player, figure, position)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)
        self.ProcessEndgame(gid, game, rv)

        return rv

    def Move(self, gid, player, fid, f, t, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.Move(player, fid, f, t)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)
        self.ProcessEndgame(gid, game, rv)

        return rv

    def Skip(self, gid, player, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.Skip(player)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)
        self.ProcessEndgame(gid, game, rv)

        return rv

    def Concede(self, gid, player, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.Concede(player)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)
        self.ProcessEndgame(gid, game, rv)

        return rv

    def ForceEnd(self, gid, player, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.ForceEnd(player)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)
        self.ProcessEndgame(gid, game, rv)

        return rv

    def Suggest(self, gid, player, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.Suggest(player)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)
        self.ProcessEndgame(gid, game, rv)

        return rv

    def ActJS_CreateGame(self, action, rv, addActions=False, addAllActions=False, addState=False):
        p1 = action["player1"]
        p2 = action["player2"]
        turn = None
        if "turn" in action:
            turn = action["turn"]

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

        tmprv = self.CreateGame(p1, p2, turn, mosquito, ladybug, pillbug, tourney, addActions, addAllActions, addState)
        tmprv.FillJson(rv)

    def ActJS_GetGames(self, action, rv):
        includeArch = False
        if "archived" in action:
            includeArch = action["archived"]

        gid = None
        players = None
        if "gid" in action:
            gid = action["gid"]
        if "players" in action:
            players = action["players"]

        tmprv = self.GetGames(includeArch, gid, players)
        tmprv.FillJson(rv)

    def ActJS_GetPlayer(self, action, rv):
        token = None
        if "token" in action:
            token = action["token"]

        telegramId = None
        if "telegramId" in action:
            telegramId = action["telegramId"]

        login = None
        password = None
        if "login" in action and "password" in action:
            login = action["login"]
            password = action["password"]

        refreshToken = None
        if "refreshToken" in action:
            refreshToken = action["refreshToken"]

        tmprv = self.GetPlayer(token, telegramId, login, password, refreshToken)
        tmprv.FillJson(rv)

    def ActJS_CreatePlayer(self, action, rv):
        name = None
        if "name" in action:
            name = action["name"]
        login = None
        if "login" in action:
            login = action["login"]
        password = None
        if "password" in action:
            password = action["password"]
        telegramId = None
        if "telegramId" in action:
            telegramId = action["telegramId"]
        premium = False
        if "premium" in action:
            premium = action["premium"]

        tmprv = self.CreatePlayer(name, login, password, telegramId, premium)
        tmprv.FillJson(rv)

    def ActJS_GetOrCreatePlayer(self, action, rv):
        token = None
        if "token" in action:
            token = action["token"]
        telegramId = None
        if "telegramId" in action:
            telegramId = action["telegramId"]
        login = None
        password = None
        if "login" in action and "password" in action:
            login = action["login"]
            password = action["password"]
        refreshToken = None
        if "refreshToken" in action:
            refreshToken = action["refreshToken"]
        name = None
        if "name" in action:
            name = action["name"]
        premium = False
        if "premium" in action:
            premium = action["premium"]

        tmprv = self.GetOrCreatePlayer(token, name, login, password, telegramId, premium, refreshToken)
        tmprv.FillJson(rv)

    def ActJS_ModifyPlayer(self, action, rv):
        token = None
        if "token" in action:
            token = action["token"]

        telegramId = None
        if "telegramId" in action:
            telegramId = action["telegramId"]

        login = None
        password = None
        if "login" in action and "password" in action:
            login = action["login"]
            password = action["password"]

        refreshToken = None
        if "refreshToken" in action:
            refreshToken = action["refreshToken"]

        newVals = action["newValues"]

        newName = None
        if "name" in newVals:
            newName = newVals["name"]
        newLogin = None
        if "login" in newVals:
            newLogin = newVals["login"]
        newPassword = None
        if "password" in newVals:
            newPassword = newVals["password"]
        newTelegramId = None
        if "telegramId" in newVals:
            newTelegramId = newVals["telegramId"]
        newPremium = None
        if "premium" in newVals:
            newPremium = newVals["premium"]

        tmprv = self.ModifyPlayer(token, telegramId, login, password, refreshToken, newName, newLogin, newPassword, newTelegramId, newPremium)
        tmprv.FillJson(rv)

    def ActJS(self, action):
        rv = {"action": action}
        try:
            act = action["action"]
            game = None
            if act == Action.CreateGame:
                game = self.ActJS_CreateGame(action, rv)
            elif act == Action.GetGames:
                self.ActJS_GetGames(action, rv)
            elif act == Action.GetPlayer:
                self.ActJS_GetPlayer(action, rv)
            elif act == Action.CreatePlayer:
                self.ActJS_CreatePlayer(action, rv)
            elif act == Action.ModifyPlayer:
                self.ActJS_ModifyPlayer(action, rv)
            elif act == Action.CreatePlayer:
                self.ActJS_CreatePlayer(action, rv)
            elif act == Action.GetOrCreatePlayer:
                self.ActJS_GetOrCreatePlayer(action, rv)
            elif act == Action.Move:
                pid = action["player"]
                gid = action["gid"]
                fid = action["fid"]
                f = action["from"]
                t = action["to"]
                addActions = False
                addState = False
                addAllActions = False
                if "addActions" in action:
                    addActions = action["addActions"]
                if "addState" in action:
                    addState = action["addState"]
                    if "addAllActions" in action:
                        addAllActions = action["addAllActions"]
                tmpRv = self.Move(gid, pid, fid, f, t, addActions, addAllActions, addState)
                tmpRv.FillJson(rv)
            elif act == Action.Place:
                pid = action["player"]
                gid = action["gid"]
                figure = action["figure"]
                position = action["position"]
                addActions = False
                addState = False
                addAllActions = False
                if "addActions" in action:
                    addActions = action["addActions"]
                if "addState" in action:
                    addState = action["addState"]
                    if "addAllActions" in action:
                        addAllActions = action["addAllActions"]

                tmpRv = self.Place(gid, pid, figure, position, addActions, addAllActions, addState)
                tmpRv.FillJson(rv)
            elif act == Action.ForceEnd:
                pid = action["player"]
                gid = action["gid"]

                addActions = False
                addState = False
                addAllActions = False
                if "addActions" in action:
                    addActions = action["addActions"]
                if "addState" in action:
                    addState = action["addState"]
                    if "addAllActions" in action:
                        addAllActions = action["addAllActions"]

                tmpRv = self.ForceEnd(gid, pid, addActions, addAllActions, addState)
                tmpRv.FillJson(rv)
            elif act == Action.Suggest:
                pid = action["player"]
                gid = action["gid"]

                addActions = False
                addState = False
                addAllActions = False
                if "addActions" in action:
                    addActions = action["addActions"]
                if "addState" in action:
                    addState = action["addState"]
                    if "addAllActions" in action:
                        addAllActions = action["addAllActions"]

                tmpRv = self.Suggest(gid, pid, addActions, addAllActions, addState)
                tmpRv.FillJson(rv)
            elif act == Action.Concede:
                pid = action["player"]
                gid = action["gid"]

                addActions = False
                addState = False
                addAllActions = False
                if "addActions" in action:
                    addActions = action["addActions"]
                if "addState" in action:
                    addState = action["addState"]
                    if "addAllActions" in action:
                        addAllActions = action["addAllActions"]

                tmpRv = self.Concede(gid, pid, addActions, addAllActions, addState)
                tmpRv.FillJson(rv)
            elif act == Action.Skip:
                pid = action["player"]
                gid = action["gid"]

                addActions = False
                addState = False
                addAllActions = False
                if "addActions" in action:
                    addActions = action["addActions"]
                if "addState" in action:
                    addState = action["addState"]
                    if "addAllActions" in action:
                        addAllActions = action["addAllActions"]

                tmpRv = self.Skip(gid, pid, addActions, addAllActions, addState)
                tmpRv.FillJson(rv)
            elif act == Action.Undefined:
                raise UnknownAction("Undefined action is not allowed")
            else:
                raise UnknownAction("Unknown action: %s" % act)

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

    def _persist_game(self, game_id):
        with self.game_state_table._meta.database.atomic():
            if game_id in self.runningGames:
                state_str = self.runningGames[game_id].serialize()

                game_state, is_created = self.game_state_table.get_or_create(id=game_id, defaults={'state': state_str})

                if not is_created:
                    game_state.state = state_str
                    game_state.save()
            else:
                self.game_state_table.delete().where(self.game_state_table.id == game_id).execute()