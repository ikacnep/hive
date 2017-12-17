import unittest
from ..GamesManipulator import GamesManipulator
from ..Game.Settings.Figures.FigureTypes import FigureType
from ..Game.Utils.Action import Action
from ..Database.TestDatabase import TestGameArchieved
from ..Database.TestDatabase import TestGame
from ..Database.TestDatabase import TestPlayer

class GameInstanceTests(unittest.TestCase):
    def setUp(self):
        if TestGameArchieved.table_exists():
            TestGameArchieved.drop_table()

        if TestGame.table_exists():
            TestGame.drop_table()

        if TestPlayer.table_exists():
            TestPlayer.drop_table()

    def tearDown(self):
        TestGameArchieved.drop_table()
        TestGame.drop_table()
        TestPlayer.drop_table()

    def testEverything(self):
        manipulator = GamesManipulator(playerType=TestPlayer, gameType=TestGame, archType=TestGameArchieved)
# Creating players
        action = {
            "action":Action.CreatePlayer,
            "name":"tester1",
            "login":"logger1",
            "password":"ffs",
            "telegramId":1,
            "premium":True
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        p1 = rv["player"]
        self.assertIsNotNone(p1)
        self.assertEqual(p1["name"], action["name"])
        self.assertEqual(p1["premium"], action["premium"])

        action = {
            "action": Action.CreatePlayer,
            "name" : "tester2",
            "login" : "logger2",
            "password" : "ffs"
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        p2 = rv["player"]
        self.assertIsNotNone(p2)
        self.assertEqual(p2["name"], action["name"])
        self.assertEqual(p2["premium"], False)

        action = {
            "action" : Action.CreatePlayer,
            "telegramId" : 2
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        p3 = rv["player"]
        self.assertIsNotNone(p3)
        self.assertEqual(p3["name"], None)
        self.assertEqual(p3["premium"], False)

        action = {
            "action" : Action.CreatePlayer,
            "telegramId" : 2
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
            "action":Action.GetPlayer,
            "login":"logger2",
            "password":"wrong"
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
            "newValues":{
                "name":"p1"
            },
            "token":p1["token"]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["player"]["name"], "p1")
        p1["name"] = rv["player"]["name"]
        for kvp in p1.items():
            self.assertEqual(kvp[1], rv["player"][kvp[0]])

# Creating Game
        action = {
            "action":Action.CreateGame,
            "player1":p1["id"],
            "player2":p2["id"],
            "turn":p1["id"]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], True)
        gid1 = rv["gid"]
        self.assertIsNotNone(gid1)
        self.assertEqual(rv["player1"], p1["id"])
        self.assertEqual(rv["player2"], p2["id"])

        action = {
            "action":Action.CreateGame,
            "player1": -1,
            "player2":p3["id"]
        }
        rv = manipulator.ActJS(action)
        self.assertEqual(rv["result"], False)
        self.assertIsNotNone(rv["reason"])
        self.assertIsNotNone(rv["message"])

        action = {
            "action":Action.CreateGame,
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
            "action":Action.GetGames,
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
            "action":Action.GetGames,
            "players":[p1["id"]]
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
            "players":[ p1["id"], p2["id"] ]
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
            "action":Action.Place,
            "gid":gid1,
            "player":p1["id"],
            "figure":FigureType.Queen,
            "position":(0, 1)
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
            "gid":gid1,
            "player":p1["id"]
        }
        rv = manipulator.ActJS(action)
        if ("message" in rv):
            self.assertEqual(rv["message"], None)
        self.assertEqual(rv["result"], True)
        self.assertTrue(rv["ended"])
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

#Finding ended game
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


if __name__ == '__main__':
    unittest.main()
