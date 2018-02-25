import json
import random
import uuid
import zlib
from typing import Dict

from .crypta import crypta
from .Database.Database import *
from .Game.GameInstance import GameInstance
from .Game.Settings.GameSettings import GameSettings
from .Game.Utils.Action import Action
from .Game.Utils.Exceptions import *
from .JsonPYAdaptors.CreateGameResult import CreateGameResult
from .JsonPYAdaptors.CreatePlayerResult import CreatePlayerResult
from .JsonPYAdaptors.GetGamesResult import GetGamesResult
from .JsonPYAdaptors.GetPlayerResult import GetPlayerResult
from .JsonPYAdaptors.ModifyPlayerResult import ModifyPlayerResult
from .Lobby import *


class GamesManipulator:
    players = None
    games = None
    archive = None
    runningGames = Dict[int, GameInstance]
    lobbys = []
    quicks = []
    lobbyid = 1
    quickid = 1

    def __init__(self, player_type=Player, game_type=Game, arch_type=GameArchieved, game_state_type=PersistedGameState):
        self.players = player_type
        if not self.players.table_exists():
            self.players.create_table()

        self.games = game_type
        if not self.games.table_exists():
            self.games.create_table()

        self.archive = arch_type
        if not self.archive.table_exists():
            self.archive.create_table()

        self.game_state_table = game_state_type
        if not self.game_state_table.table_exists():
            self.game_state_table.create_table()

        self.runningGames = {}
        for game_state in game_state_type.select():
            self.runningGames[game_state.id] = GameInstance.deserialize(game_state.state)

        self.lobbys = []
        self.quicks = []

    def CreateLobby(self, name, player, mosquito=False, ladybug=False, pillbug=False, tourney=False, duration=3600):
        try:
            p = self.players.get(self.players.id == player)
        except Exception as ex:
            raise PlayerNotFoundException("Player not found.", ex.args)

        for lobby in self.lobbys:
            if lobby.owner == player:
                return lobby

        lobby_room = LobbyRoom()
        lobby_room.id = self.lobbyid
        self.lobbyid += 1
        lobby_room.name = name
        lobby_room.owner = p.id
        lobby_room.mosquito = mosquito
        lobby_room.ladybug = ladybug
        lobby_room.pillbug = pillbug
        lobby_room.tourney = tourney
        lobby_room.creationDate = datetime.datetime.now()
        lobby_room.duration = duration
        lobby_room.expirationDate = lobby_room.creationDate + datetime.timedelta(0, lobby_room.duration)

        self.lobbys.append(lobby_room)

        return lobby_room

    def CreateQuickGame(self, player, mosquito=False, ladybug=False, pillbug=False, tourney=False):
        try:
            p = self.players.get(self.players.id == player)
        except Exception as ex:
            raise PlayerNotFoundException("Player not found.", ex.args)

        for quick in self.quicks:
            if quick.player == player:
                return quick

        quick_game = QuickGame()
        quick_game.id = self.quickid
        self.quickid += 1
        quick_game.player = p.id
        quick_game.mosquito = mosquito
        quick_game.ladybug = ladybug
        quick_game.pillbug = pillbug
        quick_game.tourney = tourney
        quick_game.rating = p.rating
        quick_game.creationDate = datetime.datetime.now()

        self.quicks.append(quick_game)

        return quick_game

    def GetLobby(self, lobby_id=None, player=None, ready=None):
        dropUs = []
        now = datetime.datetime.now()
        for l in self.lobbys:
            if l.expirationDate <= now:
                dropUs.append(l)

        for l in dropUs:
            self.lobbys.remove(l)

        rv = GetLobbyResult()
        rv.lobbys = []

        if lobby_id is not None:
            for l in self.lobbys:
                if l.id == lobby_id:
                    rv.lobbys.append(l)
                    break

        elif player is not None:
            for l in self.lobbys:
                if l.owner == player:
                    rv.lobbys.append(l)
                    break

        else:
            for theLobby in self.lobbys:
                if (ready is None) or ((theLobby.ownerReady and theLobby.guestReady) == ready):
                    rv.lobbys.append(theLobby)

        if len(rv.lobbys) == 0:
            raise LobbyNotFoundException("Lobby with specified parameters does not exist")

        return rv

    def GetQuickGame(self, player=None):
        rv = GetQuickGameResult()
        rv.quickGames = []

        if player is not None:
            for qg in self.quicks:
                if (qg.player == player) or (qg.player2 == player):
                    rv.quickGames.append(qg)
                    break

        else:
            try:
                for theQg in self.quicks:
                    rv.quickGames.append(theQg)
            except:
                rv.quickGames = []

        if len(rv.quickGames) == 0:
            raise QuickGameNotFoundException("Lobby with specified id does not exist")

        return rv

    def JoinLobby(self, lobby_id, player):
        try:
            p = self.players.get(self.players.id == player)
        except Exception as ex:
            raise PlayerNotFoundException("Player not found.", ex.args)

        lobby = None

        for a_lobby in self.lobbys:
            if a_lobby.id == lobby_id:
                lobby = a_lobby
                break

        if lobby is None:
            raise LobbyNotFoundException("Lobby with specified id does not exist")

        if lobby.owner == player:
            raise CannotJoinLobbyException("Cannot join lobby you are already in")

        if lobby.guest is not None:
            raise CannotJoinLobbyException("Selected lobby is full")

        lobby.guest = p.id
        lobby.guestReady = False
        lobby.ownerReady = False

        return lobby

    def RefreshLobby(self, lobby_id, player, mosquito=None, ladybug=None, pillbug=None, tourney=None, duration=None):
        change_me = None
        for l in self.lobbys:
            if l.id == lobby_id:
                change_me = l
                break
        if change_me is None:
            raise LobbyNotFoundException("Lobby with specified id does not exist")

        if change_me.owner != player:
            raise AccessException("Only owner can refresh lobby")

        somethingChanged = False
        if mosquito is not None:
            change_me.mosquito = mosquito
            somethingChanged = True
        if ladybug is not None:
            change_me.mosquito = ladybug
            somethingChanged = True
        if pillbug is not None:
            change_me.mosquito = pillbug
            somethingChanged = True
        if tourney is not None:
            change_me.mosquito = tourney
            somethingChanged = True
        if duration is not None:
            change_me.duration = duration

        change_me.expiryDate = datetime.datetime.now() + datetime.timedelta(0, change_me.duration)
        if somethingChanged:
            change_me.ownerReady = False
            change_me.guestReady = False

        return change_me

    def RefreshQuickGame(self, player):
        mainQ = None
        for quick in self.quicks:
            if quick.player == player or quick.player2 == player:
                mainQ = quick
                break
        if mainQ is None:
            raise QuickGameNotFoundException("Lobby with specified id does not exist")

        if mainQ.player2 is not None:
            return mainQ

        dist = (((datetime.datetime.now() - mainQ.creationDate).total_seconds() // 5) * 0.01 + 1.05) * mainQ.rating
        enemies = []
        for quick in self.quicks:
            if quick != mainQ and \
                    quick.player2 is None and \
                    quick.mosquito == mainQ.mosquito \
                    and quick.tourney == mainQ.tourney \
                    and quick.pillbug == mainQ.pillbug \
                    and quick.ladybug == mainQ.ladybug \
                    and abs(quick.rating - mainQ.rating) < dist:
                enemies.append(quick)

        if len(enemies) == 0:
            return mainQ

        enemy = random.choice(enemies)
        mainQ.player2 = enemy.player
        self.quicks.remove(enemy)

        return mainQ

    def RemoveQuickGame(self, quick_id, player):
        mainQ = None
        for q in self.quicks:
            if q.id == quick_id:
                mainQ = q
                break
        if mainQ is None:
            raise QuickGameNotFoundException("Lobby with specified id does not exist")

        if mainQ.player != player:
            raise AccessException("Only owner can stop search")

        self.quicks.remove(mainQ)

        rv = SuccessResult()
        rv.success = True

        return rv

    def LeaveLobby(self, lobby_id, player):
        lobby = None
        for l in self.lobbys:
            if l.id == lobby_id:
                lobby = l
                break
        if lobby is None:
            raise LobbyNotFoundException("Lobby with specified id does not exist")

        if lobby.guest == player:
            lobby.guest = None
            lobby.guestReady = False
        elif lobby.owner == player:
            self.lobbys.remove(lobby)
        else:
            raise AccessException("Cannot leave lobby you are not in")

        rv = SuccessResult()
        rv.success = True

        return rv

    def ReadyLobby(self, lobby_id, player):
        lobby = None
        for l in self.lobbys:
            if l.id == lobby_id:
                lobby = l
                break
        if lobby is None:
            raise LobbyNotFoundException("Lobby with specified id does not exist")

        if lobby.guest == player:
            lobby.guestReady = True
        elif lobby.owner == player:
            lobby.ownerReady = True
        else:
            raise AccessException("Cannot ready in lobby you are not in")

        rv = SuccessResult()
        rv.success = True

        return rv

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

        quick = None
        for q in self.quicks:
            if (q.player == p1.id or q.player2 == p1.id) and (q.player == p2.id or q.player2 == p2.id):
                quick = q
                break
        if quick is not None:
            self.quicks.remove(quick)

        lobby = None
        for l in self.lobbys:
            if (l.owner == p1.id or l.guest == p1.id) and (l.owner == p2.id or l.guest == p2.id):
                lobby = l
                break
        if lobby is not None:
            self.lobbys.remove(lobby)

        return actualGame

    def CreateGame(self, player1, player2, turn=None, mosquito=False, ladybug=False, pillbug=False, tourney=False,
                   addActions=False, addAllActions=False, addState=False):
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

        rv.games = []

        if gid is not None:
            if gid in self.runningGames:
                theGame = self.games.get(self.games.id == gid)
                rv.games.append(Game.ToClass(theGame))
            elif includeArch:
                theGame = self.archive.get(self.archive.gameid == gid)
                rv.games.append(GameArchieved.ToClass(theGame))
        else:
            if players is not None:
                try:
                    p1 = self.players.get(self.players.id == players[0])
                    p2 = None
                    if len(players) > 1:
                        p2 = self.players.get(self.players.id == players[1])
                except Exception as ex:
                    raise PlayerNotFoundException("Player with specified ID not found", ex.args)

                if p2 is None:
                    try:
                        for theGame in self.games.select().where(
                                (self.games.player1 == p1) | (self.games.player2 == p1)
                        ):
                            rv.games.append(Game.ToClass(theGame))
                    except Exception:
                        pass
                    if includeArch:
                        try:
                            for theGame in self.archive.select().where(
                                    (self.archive.player1 == p1) | (self.archive.player2 == p1)
                            ):
                                rv.games.append(GameArchieved.ToClass(theGame))
                        except:
                            pass
                else:
                    try:
                        for theGame in self.games.select().where(
                                ((self.games.player1 == p1) & (self.games.player2 == p2))
                                | ((self.games.player1 == p2) & (self.games.player2 == p1))
                        ):
                            rv.games.append(Game.ToClass(theGame))
                    except:
                        pass

                    if includeArch:
                        try:
                            for theGame in self.archive.select().where(
                                    ((self.archive.player1 == p1) & (self.archive.player2 == p2))
                                    | ((self.archive.player1 == p2) & (self.archive.player2 == p1))
                            ):
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

        return rv

    def GetPlayerInner(self, pid=None, token=None, telegramId=None, login=None, password=None, refreshToken=False):
        player = None
        try:
            if pid is not None:
                player = self.players.get(self.players.id == pid)
            elif token is not None:
                player = self.players.get(self.players.token == token)
            elif telegramId is not None:
                player = self.players.get(self.players.telegramId == telegramId)
            elif login is not None and password is not None:
                player = self.players.get(self.players.login == login)

                crypta.check_password(password, player.password_enc)

        except Exception as ex:
            raise PlayerNotFoundException("Player with specified parameters not found", ex.args)

        if player is None:
            raise PlayerNotFoundException("Necessary parameters not specified")

        if refreshToken:
            player.token = str(self.GetToken())
            player.save()

        return player

    def GetPlayer(self, pid=None, token=None, telegramId=None, login=None, password=None, refreshToken=False):
        rv = GetPlayerResult()

        player = self.GetPlayerInner(pid, token, telegramId, login, password, refreshToken)
        rv.player = Player.ToClass(player)

        return rv

    def CreatePlayer(self, name=None, login=None, password=None, telegramId=None, premium=False):
        rv = CreatePlayerResult()

        if login is not None:
            p = None
            try:
                p = self.players.get(self.players.login == login)
            except:
                pass
            if p is not None:
                raise PlayerCreationException("Login is already in use")

        if telegramId is not None:
            p = None
            try:
                p = self.players.get(self.players.telegramId == telegramId)
            except Exception:
                pass

            if p is not None:
                raise PlayerCreationException("This telegramid is already in use")

        if login is None and telegramId is None:
            raise PlayerCreationException(
                "Cannot create player without login and telegram id. No way for him to join the club")

        password_enc = None
        if password:
            password_enc = crypta.scramble_password(password)

        p = self.players.create(
            name=name,
            login=login,
            password_enc=password_enc,
            telegramId=telegramId,
            premium=premium,
            token=str(self.GetToken())
        )
        rv.player = Player.ToClass(p)

        return rv

    def GetOrCreatePlayer(self, token=None, name=None, login=None, password=None, telegramId=None, premium=False,
                          refreshToken=False):
        rv = self.GetPlayer(None, token, telegramId, login, password, refreshToken)
        if not rv.result:
            rv = self.CreatePlayer(name, login, password, telegramId, premium)

        return rv

    def ModifyPlayer(self, pid=None, token=None, telegramId=None, login=None, password=None, refreshToken=False,
                     newName=None, newLogin=None, newPassword=None, newTelegramId=None, newPremium=None):
        rv = ModifyPlayerResult()

        p = self.GetPlayerInner(pid, token, telegramId, login, password, refreshToken)

        if newLogin is not None and newLogin != login:
            tmpP = None
            try:
                tmpP = self.players.get(self.players.login == newLogin)
            except:
                pass
            if tmpP is not None:
                raise PlayerModificationException("login is already in use")
            p.login = newLogin

        if newName is not None:
            p.name = newName
        if newPassword is not None:
            p.password_enc = crypta.scramble_password(newPassword)
        if newTelegramId is not None:
            tmpP = None
            try:
                tmpP = self.players.get(self.players.telegramId == newTelegramId)
            except:
                pass
            if tmpP is not None:
                raise PlayerModificationException("telegram ID is already in use")
            p.telegramId = newTelegramId
        if newPremium is not None:
            p.premium = newPremium

        p.save()

        rv.player = Player.ToClass(p)

        return rv

    def GetGameInst(self, gid) -> GameInstance:
        if gid not in self.runningGames:
            raise GameNotFoundException("No such ID in running games")
        gameInst = self.runningGames[gid]

        return gameInst

    def _DoEndGame(self, gid, gameInst, rv):
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

        self._persist_game(gid)

        return rv

    def Move(self, gid, player, fid, f, t, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.Move(player, fid, f, t)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)

        self._persist_game(gid)

        return rv

    def Skip(self, gid, player, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.Skip(player)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)

        self._persist_game(gid)

        return rv

    def Concede(self, gid, player, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.Concede(player)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)

        self._persist_game(gid)

        return rv

    def ForceEnd(self, gid, player, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.ForceEnd(player)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)

        self._persist_game(gid)

        return rv

    def Suggest(self, gid, player, addActions=False, addAllActions=False, addState=False):
        game = self.GetGameInst(gid)
        rv = game.Suggest(player)
        if addActions:
            rv.actions = game.GetActions()
        if addState:
            rv.state = game.GetState(addAllActions=addAllActions)

        self._persist_game(gid)

        return rv

    def CloseGame(self, gid):
        game = self.runningGames.pop(gid)
        rv = game.CloseGame()

        self._DoEndGame(gid, game, rv)

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
        pid = action.get('id')

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

        tmprv = self.GetPlayer(pid, token, telegramId, login, password, refreshToken)
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
        pid = action.get('id')

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

        tmprv = self.ModifyPlayer(pid, token, telegramId, login, password, refreshToken, newName, newLogin, newPassword,
                                  newTelegramId, newPremium)
        tmprv.FillJson(rv)

    def ActJS(self, action):
        rv = {"action": action}
        try:
            act = action["action"]
            if act == Action.CreateGame:
                self.ActJS_CreateGame(action, rv)
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
            elif act == Action.CloseGame:
                gid = action["gid"]
                tmpRv = self.CloseGame(gid)
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
        q1 = pow(10, rate1 / 400)
        q2 = pow(10, rate2 / 400)
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
