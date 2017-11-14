from Database.Database import *
from Game.Utils.Exceptions import *
from Game.GameInstance import GameInstance
from Game.Settings.GameSettings import GameSettings
from Game.Utils.Action import Action
from peewee import *
import random
import zlib
import json
import uuid

class GamesManipulator:
    players = None
    games = None
    archive = None
    runningGames = {}
    initialized = False

    @staticmethod
    def Init(playerType=Player, gameType=Game, archType=GameArchieved):
        if GamesManipulator.initialized:
            return

        GamesManipulator.players = playerType
        if not GamesManipulator.players.table_exists():
            GamesManipulator.players.create_table()

        GamesManipulator.games = gameType
        if not GamesManipulator.games.table_exists():
            GamesManipulator.games.create_table()

        GamesManipulator.archive = archType
        if not GamesManipulator.archive.table_exists():
            GamesManipulator.archive.create_table()

        GamesManipulator.runningGames = {}
        GamesManipulator.initialized = True

    @staticmethod
    def CreateGame(player1, player2, mosquito, ladybug, pillbug, tourney, rv):
        if not GamesManipulator.initialized:
            GamesManipulator.Init()

        try:
            p1 = GamesManipulator.players.get(GamesManipulator.players.id == player1)
            p2 = GamesManipulator.players.get(GamesManipulator.players.id == player2)
        except Exception as ex:
            raise PlayerNotFoundException("Player not found.", ex.args)

        game = GamesManipulator.games.create(player1=p1, player2=p2)
        actualGame = GameInstance(player1, player2,
                                  GameSettings.GetSettings(mosquito=mosquito, ladybug=ladybug, pillbug=pillbug,
                                                           tourney=tourney))
        GamesManipulator.runningGames[game.id] = actualGame

        rv["gid"] = game.id
        rv["player1"] = player1
        rv["player2"] = player2

        return actualGame

    @staticmethod
    def Act_CreateGame(action, rv):
        p1 = action["player1"]
        p2 = action["player2"]
        turn = None
        if "turn" in action:
            turn = action["turn"]
            if turn != p1 and turn != p2:
                turn = None

        if turn == None:
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

        return GamesManipulator.CreateGame(p1, p2, mosquito, ladybug, pillbug, tourney, rv)

    @staticmethod
    def Act_GetGames(action, rv):
        try:
            includeArch = False
            if "archived" in action:
                includeArch = action["archived"]

            rv["games"] = []
            if "gid" in action:
                gid = action["gid"]
                if gid in GamesManipulator.runningGames:
                    theGame = GamesManipulator.games.get(GamesManipulator.games.id == gid)
                    rv["games"].append(Game.ToHash(theGame))
                elif includeArch:
                    theGame = GamesManipulator.archive.get(GamesManipulator.archive.gameid == gid)
                    rv["games"].append(GameArchieved.ToHash(theGame))
            else:
                if "players" in action:
                    players = action["players"]
                    try:
                        p1 = GamesManipulator.players.get(GamesManipulator.players.id == players[0])
                        p2 = None
                        if (len(players) > 1):
                            p2 = GamesManipulator.players.get(GamesManipulator.players.id == players[1])
                    except Exception as ex:
                        raise PlayerNotFoundException("Player with specified ID not found", ex.args)

                    if p2 == None:
                        try:
                            for theGame in GamesManipulator.games.select().where(
                                                    GamesManipulator.games.player1 == p1 or GamesManipulator.games.player2 == p1):
                                rv["games"].append(Game.ToHash(theGame))
                        except Exception as ex:
                            pass
                        if includeArch:
                            try:
                                for theGame in GamesManipulator.archive.select().where(
                                                        GamesManipulator.archive.player1 == p1 or GamesManipulator.archive.player2 == p1):
                                    rv["games"].append(GameArchieved.ToHash(theGame))
                            except:
                                pass
                    else:
                        try:
                            for theGame in GamesManipulator.games.select().where((
                                                         GamesManipulator.games.player1 == p1 and GamesManipulator.games.player2 == p2) or
                                                         (
                                                                 GamesManipulator.games.player1 == p2 and GamesManipulator.games.player2 == p1)):
                                rv["games"].append(Game.ToHash(theGame))
                        except:
                            pass
                        if includeArch:
                            try:
                                for theGame in GamesManipulator.archive.select().where(
                                                (
                                                        GamesManipulator.archive.player1 == p1 and GamesManipulator.archive.player2 == p2) or
                                                (
                                                        GamesManipulator.archive.player1 == p2 and GamesManipulator.archive.player2 == p1)):
                                    rv["games"].append(GameArchieved.ToHash(theGame))
                            except:
                                pass
                else:
                    rv["games"] = []
                    for theGame in GamesManipulator.games.select():
                        rv["games"].append(Game.ToHash(theGame))
                    if includeArch:
                        for theGame in GamesManipulator.archive.select():
                            rv["games"].append(GameArchieved.ToHash(theGame))

            if len(rv["games"]) == 0:
                raise GameNotFoundException("Game with specified parameters not found")
        except PlayerNotFoundException as ex:
            raise ex
        except Exception as ex:
            raise GameNotFoundException("Game with specified parameters not found", ex.args)

    @staticmethod
    def Act_GetPlayer(action, rv):
        player = None
        try:
            if "token" in action:
                token = action["token"]
                player = GamesManipulator.players.get(GamesManipulator.players.token == token)
            elif "telegramId" in action:
                telegramId = action["telegramId"]
                player = GamesManipulator.players.get(GamesManipulator.players.telegramId == telegramId)
            elif "login" in action and "password" in action:
                login = action["login"]
                password = action["password"]
                player = GamesManipulator.players.get(
                    GamesManipulator.players.login == login and GamesManipulator.players.password == password)
        except Exception as ex:
            raise PlayerNotFoundException("Player with specified parameters not found", ex.args)
        if player == None:
            raise PlayerNotFoundException("Necessary parameters not specified")


        if "refreshToken" in action and action["refreshToken"]:
            player.token = str(GamesManipulator.GetToken())
            player.save()
        rv["player"] = Player.ToHash(player)

        return player

    @staticmethod
    def Act_CreatePlayer(action, rv):
        name = None
        if "name" in action:
            name = action["name"]
        login = None
        if "login" in action:
            p = None
            login = action["login"]
            try:
                p = GamesManipulator.players.get(GamesManipulator.players.login == login)
            except:
                pass
            if p != None:
                raise PlayerCreationException("Login is already in use")
        password = None
        if "password" in action:
            password = action["password"]
        telegramId = None
        if "telegramId" in action:
            telegramId = action["telegramId"]
            p = None
            try:
                p = GamesManipulator.players.get(GamesManipulator.players.telegramId == telegramId)
            except Exception as ex:
                pass

            if p != None:
                raise PlayerCreationException("This telegramid is already in use")
        premium = False
        if "premium" in action:
            premium = action["premium"]

        p = GamesManipulator.players.create(
            name=name,
            login=login,
            password=password,
            telegramId=telegramId,
            premium=premium,
            token=str(GamesManipulator.GetToken())
        )
        rv["player"] = Player.ToHash(p)

    @staticmethod
    def Act_DoAction(action, rv):
        gid = action["gid"]
        if gid not in GamesManipulator.runningGames:
            raise GameNotFoundException("No such ID in running games")
        gameInst = GamesManipulator.runningGames[gid]
        gameInst.Act(action, False, False, rv)
        rv["gid"] = gid
        if (rv["ended"]):
            GamesManipulator.runningGames.pop(gid)
            try:
                p1 = GamesManipulator.players.get(GamesManipulator.players.id == gameInst.player0)
                p2 = GamesManipulator.players.get(GamesManipulator.players.id == gameInst.player1)
            except Exception as ex:
                raise PlayerNotFoundException("Player not found.", ex.args)

            try:
                game = GamesManipulator.games.get(GamesManipulator.games.id == gid)
            except Exception as ex:
                raise GameNotFoundException("No such ID in database.", ex.args)

            res = 0
            if rv["lost"][p1.id]:
                res += 1
            if rv["lost"][p2.id]:
                res -= 1
            ratingChange = GamesManipulator.GetEloRate(p1.rating, p2.rating, res)

            GamesManipulator.archive.create(
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
            p1.save()
            p2.save()
            rv["rateChange"] = {
                p1.id: ratingChange[0],
                p2.id: ratingChange[1]
            }

        return gameInst

    @staticmethod
    def Act_ModifyPlayer(action, rv):
        tmp = {}
        p = GamesManipulator.Act_GetPlayer(action, tmp)

        newVals = action["newValues"]
        if "name" in newVals:
            p.name = newVals["name"]
        if "login" in newVals:
            log = newVals["login"]
            if log != p.login:
                tmpP = None
                try:
                    tmpP = GamesManipulator.players.get(GamesManipulator.players.login == log)
                except:
                    pass
                if tmpP != None:
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

    @staticmethod
    def Act(action):
        rv = {"action":action}
        try:
            act = action["action"]
            game = None
            if (act == Action.CreateGame):
                game = GamesManipulator.Act_CreateGame(action, rv)
            elif act == Action.GetGames:
                GamesManipulator.Act_GetGames(action, rv)
            elif act == Action.GetPlayer:
                GamesManipulator.Act_GetPlayer(action, rv)
            elif act == Action.CreatePlayer:
                GamesManipulator.Act_CreatePlayer(action, rv)
            elif act == Action.ModifyPlayer:
                GamesManipulator.Act_ModifyPlayer(action, rv)
            elif act in (Action.Move, Action.Place, Action.ForceEnd, Action.Suggest, Action.Concede, Action.Skip):
                game = GamesManipulator.Act_DoAction(action, rv)
            elif act == Action.Undefined:
                raise UnknownAction("Undefined action is not allowed")

            if "addActions" in action and game != None and action["addActions"]:
                rv["actions"] = game.GetActions()
            if "addState" in action and game != None and action["addState"]:
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

    @staticmethod
    def GetToken():
        while True:
            newToken = uuid.uuid4()
            try:
                p = GamesManipulator.players.get(GamesManipulator.players.token == newToken)
                if (p == None):
                    return newToken
            except:
                return newToken
