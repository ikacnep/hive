import unittest

from time import sleep

from spine.Game.Utils.Exceptions import *
from ..Database.TestDatabase import *
from ..Game.Settings.Figures.FigureTypes import FigureType
from ..Game.Utils.Action import Action
from ..GamesManipulator import GamesManipulator


class GameInstanceTests(unittest.TestCase):
    def setUp(self):
        for table in (TestGameArchieved, TestGame, TestPlayer, TestPersistedGameState):
            if table.table_exists():
                table.drop_table()

    def tearDown(self):
        for table in (TestGameArchieved, TestGame, TestPlayer, TestPersistedGameState):
            table.drop_table()

    def testEverything(self):
        manipulator = GamesManipulator(
            player_type=TestPlayer,
            game_type=TestGame,
            arch_type=TestGameArchieved,
            game_state_type=TestPersistedGameState
        )

        # Creating players
        action = {
            "action": Action.CreatePlayer,
            "name": "tester1",
            "login": "logger1",
            "password": "ffs",
            "telegramId": 1,
            "premium": True
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        p1 = rv["player"]
        self.assertIsNotNone(p1)
        self.assertEqual(p1["name"], action["name"])
        self.assertEqual(p1["premium"], action["premium"])

        action = {
            "action": Action.CreatePlayer,
            "name": "tester2",
            "login": "logger2",
            "password": "ffs"
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        p2 = rv["player"]
        self.assertIsNotNone(p2)
        self.assertEqual(p2["name"], action["name"])
        self.assertEqual(p2["premium"], False)

        action = {
            "action": Action.CreatePlayer,
            "telegramId": 2
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        p3 = rv["player"]
        self.assertIsNotNone(p3)
        self.assertEqual(p3["name"], None)
        self.assertEqual(p3["premium"], False)

        action = {
            "action": Action.CreatePlayer,
            "telegramId": 2
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], False)
        self.assertIsNotNone(rv["reason"])
        self.assertIsNotNone(rv["message"])

        action = {
            "action": Action.CreatePlayer,
            "login": "logger1",
            "password": "pass"
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], False)
        self.assertIsNotNone(rv["reason"])
        self.assertIsNotNone(rv["message"])

        # Getting players
        action = {
            "action": Action.GetPlayer,
            "login": "logger2",
            "password": "wrong"
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], False)
        self.assertIsNotNone(rv["reason"])
        self.assertIsNotNone(rv["message"])

        action = {
            "action": Action.GetPlayer,
            "login": "logger1",
            "password": "ffs"
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        for kvp in p1.items():
            self.assertEqual(kvp[1], rv["player"][kvp[0]])

        action = {
            "action": Action.GetPlayer,
            "telegramId": 2
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        for kvp in p3.items():
            self.assertEqual(kvp[1], rv["player"][kvp[0]])

        action = {
            "action": Action.GetPlayer,
            "token": p2["token"],
            "refreshToken": True
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        self.assertNotEqual(p2["token"], rv["player"]["token"])
        p2["token"] = rv["player"]["token"]
        for kvp in p2.items():
            self.assertEqual(kvp[1], rv["player"][kvp[0]])

        # Modifying player
        action = {
            "action": Action.ModifyPlayer,
            "newValues": {
                "name": "p1"
            },
            "token": p1["token"]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["player"]["name"], "p1")
        p1["name"] = rv["player"]["name"]
        for kvp in p1.items():
            self.assertEqual(kvp[1], rv["player"][kvp[0]])

        # Creating Game
        action = {
            "action": Action.CreateGame,
            "player1": p1["id"],
            "player2": p2["id"],
            "turn": p1["id"]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        gid1 = rv["gid"]
        self.assertIsNotNone(gid1)
        self.assertEqual(rv["player1"], p1["id"])
        self.assertEqual(rv["player2"], p2["id"])

        action = {
            "action": Action.CreateGame,
            "player1": -1,
            "player2": p3["id"]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], False)
        self.assertIsNotNone(rv["reason"])
        self.assertIsNotNone(rv["message"])

        action = {
            "action": Action.CreateGame,
            "player1": p1["id"],
            "player2": p3["id"],
            "turn": p3["id"]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        gid2 = rv["gid"]
        self.assertIsNotNone(gid1)
        self.assertEqual(rv["player1"], p3["id"])
        self.assertEqual(rv["player2"], p1["id"])

        # Finding game
        action = {
            "action": Action.GetGames,
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        games = rv["games"]
        self.assertEqual(len(games), 2)
        for key in games:
            if key["gid"] == gid1:
                self.assertEqual(key["player1"], p1["id"])
                self.assertEqual(key["player2"], p2["id"])
            elif key["gid"] == gid2:
                self.assertEqual(key["player1"], p3["id"])
                self.assertEqual(key["player2"], p1["id"])
            else:
                self.assertTrue(False)

        action = {
            "action": Action.GetGames,
            "players": [p1["id"]]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        games = rv["games"]
        for key in games:
            if key["gid"] == gid1:
                self.assertEqual(key["player1"], p1["id"])
                self.assertEqual(key["player2"], p2["id"])
            elif key["gid"] == gid2:
                self.assertEqual(key["player1"], p3["id"])
                self.assertEqual(key["player2"], p1["id"])
            else:
                self.assertTrue(False)

        action = {
            "action": Action.GetGames,
            "players": [p1["id"], p2["id"]]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        self.assertEqual(len(rv["games"]), 1)
        self.assertEqual(rv["games"][0]["gid"], gid1)
        self.assertEqual(rv["games"][0]["hasEnded"], False)

        action = {
            "action": Action.GetGames,
            "players": [-1]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], False)
        self.assertIsNotNone(rv["message"])
        self.assertIsNotNone(rv["reason"])

        # Playing a game
        action = {
            "action": Action.Place,
            "gid": gid1,
            "player": p1["id"],
            "figure": FigureType.Queen,
            "position": (0, 1)
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], False)
        self.assertIsNotNone(rv["message"])
        self.assertIsNotNone(rv["reason"])

        action = {
            "action": Action.Place,
            "gid": gid1,
            "player": p1["id"],
            "figure": FigureType.Queen,
            "position": (0, 0)
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)

        action = {
            "action": Action.Place,
            "gid": gid2,
            "player": p2["id"],
            "figure": FigureType.Queen,
            "position": (0, 0)
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], False)
        self.assertIsNotNone(rv["message"])
        self.assertIsNotNone(rv["reason"])

        action = {
            "action": Action.Concede,
            "gid": gid1,
            "player": p1["id"]
        }
        rv = manipulator.ActJS(action)

        if "message" in rv:
            self.assertEqual(rv["message"], None)
        self.assertEqual(rv["result"], True)
        self.assertTrue(rv["ended"])

        rv = manipulator.ActJS({"action": Action.CloseGame, "gid": gid1})

        self.assertEqual(rv["result"], True)
        self.assertTrue(rv["rateChange"][p1["id"]] < 0)
        self.assertTrue(rv["rateChange"][p2["id"]] > 0)

        action = {
            "action": Action.Place,
            "gid": gid1,
            "player": p2["id"],
            "figure": FigureType.Queen,
            "position": (0, 1)
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], False)
        self.assertIsNotNone(rv["message"])
        self.assertIsNotNone(rv["reason"])

        # Finding ended game
        action = {
            "action": Action.GetGames,
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        games = rv["games"]
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["gid"], gid2)

        action = {
            "action": Action.GetGames,
            "archived": True
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        games = rv["games"]
        self.assertEqual(len(games), 2)
        for key in games:
            if key["gid"] == gid1:
                self.assertEqual(key["player1"], p1["id"])
                self.assertEqual(key["player2"], p2["id"])
                self.assertEqual(key["length"], 1)
            elif key["gid"] == gid2:
                self.assertEqual(key["player1"], p3["id"])
                self.assertEqual(key["player2"], p1["id"])
            else:
                self.assertTrue(False)

        # Checking rating change

        action = {
            "action": Action.GetPlayer,
            "login": "logger1",
            "password": "ffs"
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        p1 = rv["player"]

        action = {
            "action": Action.GetPlayer,
            "telegramId": 2
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        p3 = rv["player"]

        action = {
            "action": Action.GetPlayer,
            "token": p2["token"],
            "refreshToken": True
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        p2 = rv["player"]

        self.assertTrue(p1["rating"] < p3["rating"])
        self.assertTrue(p3["rating"] < p2["rating"])

    def testGameStatePersistence(self):
        def create_manipulator():
            return GamesManipulator(
                player_type=TestPlayer,
                game_type=TestGame,
                arch_type=TestGameArchieved,
                game_state_type=TestPersistedGameState
            )

        manipulator = create_manipulator()

        player1 = manipulator.CreatePlayer(name='player 1', telegramId=73571).player
        player2 = manipulator.CreatePlayer(name='player 2', telegramId=73572).player

        game_id = manipulator.CreateGame(player1.id, player2.id, player1.id, tourney=False).gid

        # Imitates server restart and checks that game is restored correctly
        def verify_game_instance():
            new_manipulator = create_manipulator()

            running_game = manipulator.GetGameInst(game_id)
            reloaded_game = new_manipulator.GetGameInst(game_id)

            self.assertEqual(running_game, reloaded_game)

        verify_game_instance()

        white_queen = manipulator.Place(game_id, player1.id, FigureType.Queen, (0, 0)).fid
        verify_game_instance()

        manipulator.Place(game_id, player2.id, FigureType.Queen, (0, 1))
        verify_game_instance()

        manipulator.Move(game_id, player1.id, white_queen, (0, 0), (1, 0))
        verify_game_instance()

        manipulator.Concede(game_id, player2.id)
        verify_game_instance()

        manipulator.CloseGame(game_id)

        with self.assertRaises(GameNotFoundException):
            manipulator.GetGameInst(game_id)

        with self.assertRaises(GameNotFoundException):
            create_manipulator().GetGameInst(game_id)

    def testLobby(self):
        def create_manipulator():
            return GamesManipulator(
                player_type=TestPlayer,
                game_type=TestGame,
                arch_type=TestGameArchieved,
                game_state_type=TestPersistedGameState
            )

        manipulator = create_manipulator()

        player1 = manipulator.CreatePlayer(name='player 1', telegramId=73571).player
        player2 = manipulator.CreatePlayer(name='player 2', telegramId=73572).player
        player3 = manipulator.CreatePlayer(name='player 3', telegramId=73573).player

        l1 = manipulator.CreateLobby("Test1", player1.id, duration=1)
        self.assertEqual(l1.owner, player1.id)
        self.assertEqual(l1.mosquito, False)
        self.assertEqual(l1.tourney, False)
        self.assertEqual(l1.ladybug, False)
        self.assertEqual(l1.pillbug, False)

        l2 = manipulator.CreateLobby("Test2", player2.id)

        with self.assertRaises(Exception):
             manipulator.CreateLobby("Test2", -1)

        ltmp =  manipulator.CreateLobby("Test3", player1.id, True)
        self.assertEqual(l1, ltmp)

        gl = manipulator.GetLobby()
        self.assertEqual(len(gl.lobbys), 2)

        gl = manipulator.GetLobby(lobby_id=l1.id)
        self.assertEqual(len(gl.lobbys), 1)
        self.assertEqual(gl.lobbys[0], l1)

        gl = manipulator.GetLobby(player=player2.id)
        self.assertEqual(len(gl.lobbys), 1)
        self.assertEqual(gl.lobbys[0], l2)

        gl = manipulator.GetLobby(ready=False)
        self.assertEqual(len(gl.lobbys), 2)

        with self.assertRaises(Exception):
            manipulator.GetLobby(ready=True)

        with self.assertRaises(Exception):
            manipulator.JoinLobby(l1.id, -1)

        with self.assertRaises(Exception):
            manipulator.JoinLobby(-1, player1.id)

        with self.assertRaises(Exception):
            manipulator.JoinLobby(l1.id, player1.id)

        ltmp = manipulator.JoinLobby(l1.id, player2.id)
        self.assertEqual(ltmp.owner, player1.id)
        self.assertEqual(ltmp.guest, player2.id)

        with self.assertRaises(Exception):
            manipulator.JoinLobby(l1.id, player3.id)

        with self.assertRaises(Exception):
            manipulator.RefreshLobby(-1, player1.id)

        with self.assertRaises(Exception):
            manipulator.RefreshLobby(l1.id, player2.id)

        manipulator.ReadyLobby(l1.id, player2.id)
        self.assertEqual(ltmp.ownerReady, False)
        self.assertEqual(ltmp.guestReady, True)

        ltmp = manipulator.RefreshLobby(l1.id, player1.id, mosquito=True)
        self.assertEqual(ltmp.mosquito, True)
        self.assertEqual(ltmp.ownerReady, False)
        self.assertEqual(ltmp.guestReady, False)

        manipulator.ReadyLobby(l1.id, player2.id)
        manipulator.ReadyLobby(l1.id, player1.id)
        self.assertEqual(ltmp.ownerReady, True)
        self.assertEqual(ltmp.guestReady, True)

        gl = manipulator.GetLobby(ready=True)
        self.assertEqual(len(gl.lobbys), 1)
        self.assertEqual(gl.lobbys[0].id, l1.id)

        sleep(2)

        gl = manipulator.GetLobby(ready=False)
        self.assertEqual(len(gl.lobbys), 1)
        self.assertEqual(gl.lobbys[0].id, l2.id)

        manipulator.JoinLobby(l2.id, player3.id)
        game_id = manipulator.CreateGame(player2.id, player3.id, player2.id, tourney=False).gid

        with self.assertRaises(Exception):
            manipulator.GetLobby(ready=True)

        with self.assertRaises(Exception):
            manipulator.GetLobby(ready=False)

    def testQuickmatch(self):
        def create_manipulator():
            return GamesManipulator(
                player_type=TestPlayer,
                game_type=TestGame,
                arch_type=TestGameArchieved,
                game_state_type=TestPersistedGameState
            )

        manipulator = create_manipulator()

        player1 = manipulator.CreatePlayer(name='player 1', telegramId=73571).player
        player2 = manipulator.CreatePlayer(name='player 2', telegramId=73572).player

        with self.assertRaises(Exception):
            manipulator.GetQuickGame()

        q1 = manipulator.CreateQuickGame(player1.id)
        self.assertEqual(q1.player, player1.id)
        self.assertEqual(q1.mosquito, False)
        self.assertEqual(q1.tourney, False)
        self.assertEqual(q1.ladybug, False)
        self.assertEqual(q1.pillbug, False)

        with self.assertRaises(Exception):
            manipulator.GetQuickGame(player=player2.id)

        with self.assertRaises(Exception):
            manipulator.RefreshQuickGame(player2.id)

        qtmp = manipulator.RefreshQuickGame(player1.id)
        self.assertIsNone(qtmp.player2)
        self.assertEqual(qtmp.player, player1.id)

        q2 = manipulator.CreateQuickGame(player2.id)

        with self.assertRaises(Exception):
             manipulator.CreateQuickGame(-1)

        self.assertNotEqual(q1.id, q2.id)

        qtmp = manipulator.CreateQuickGame(player1.id)
        self.assertEqual(qtmp, q1)

        gl = manipulator.GetQuickGame()
        self.assertEqual(len(gl.quickGames), 2)

        gl = manipulator.GetQuickGame(player=player1.id)
        self.assertEqual(len(gl.quickGames), 1)
        self.assertEqual(gl.quickGames[0], q1)

        qtmp = manipulator.RefreshQuickGame(player1.id)
        self.assertEqual(qtmp.player2, player2.id)
        self.assertEqual(qtmp.player, player1.id)

        gl = manipulator.GetQuickGame()
        self.assertEqual(len(gl.quickGames), 1)
        self.assertEqual(gl.quickGames[0], q1)

        gl = manipulator.GetQuickGame(player=player2.id)
        self.assertEqual(len(gl.quickGames), 1)
        self.assertEqual(gl.quickGames[0], q1)

        gl = manipulator.GetQuickGame(player=player1.id)
        self.assertEqual(len(gl.quickGames), 1)
        self.assertEqual(gl.quickGames[0], q1)

        with self.assertRaises(Exception):
             manipulator.RemoveQuickGame(-1, player1)

        with self.assertRaises(Exception):
             manipulator.RemoveQuickGame(q1.id, -1)

        with self.assertRaises(Exception):
            manipulator.RemoveQuickGame(q1.id, player2)

        manipulator.RemoveQuickGame(q1.id, player1.id)

        with self.assertRaises(Exception):
            manipulator.GetQuickGame()

        manipulator.CreateQuickGame(player1.id)
        manipulator.CreateQuickGame(player2.id)
        gl = manipulator.GetQuickGame()
        self.assertEqual(len(gl.quickGames), 2)

        manipulator.RefreshQuickGame(player2.id)
        gl = manipulator.GetQuickGame()
        self.assertEqual(len(gl.quickGames), 1)

        manipulator.CreateGame(player1.id, player2.id, player1.id)
        with self.assertRaises(Exception):
            manipulator.GetQuickGame()


if __name__ == '__main__':
    unittest.main()
