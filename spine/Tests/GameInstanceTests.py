import unittest
from ..Game.Settings.GameSettings import GameSettings
from ..Game.GameInstance import GameInstance
from ..Game.Settings.Figures.FigureTypes import FigureType
from ..Game.Utils.Action import Action
from ..Game.Utils.Exceptions import *

class GameInstanceTests(unittest.TestCase):
    def testStuff(self):
        game = GameInstance(10, 11, GameSettings.GetSettings())
        action = {
            "action": Action.Undefined
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertNotEqual(result["reason"], UnknownAction)
        self.assertIsNotNone(result["message"])

        action = {
            "player": 0,
            "action": Action.Undefined
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertNotEqual(result["reason"], UnknownAction)
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": -1
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertEqual(result["reason"], UnknownAction)
        self.assertIsNotNone(result["message"])

    def testUndefined(self):
        game = GameInstance(10, 11, GameSettings.GetSettings())
        action = {
            "player":10,
            "action":Action.Undefined
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertEqual(result["reason"], UnknownAction)
        self.assertIsNotNone(result["message"])

    def testPlacement(self):
        game = GameInstance(10, 11, GameSettings.GetSettings())
        action = {
            "player":10,
            "action":Action.Place
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action":Action.Place,
            "figure":FigureType.Queen
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Place,
            "figure": FigureType.Ant
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Place,
            "position": (0, 0)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Place,
            "figure": -1,
            "position": (0, 0)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Place,
            "figure": FigureType.Ant,
            "position": (0, 0)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], True)
        self.assertIsNotNone(result["fid"])

    def testMove(self):
        game = GameInstance(10, 11, GameSettings.GetSettings())
        action = {
            "player": 10,
            "action": Action.Place,
            "figure": FigureType.Queen,
            "position": (0, 0)
        }
        result = game.Act(action)
        q1 = result["fid"]

        action["player"] = 11
        action["position"] = (1, 0)
        result = game.Act(action)
        q2 = result["fid"]
        self.assertNotEqual(q1, q2)

        action = {
            "player": 11,
            "action": Action.Move,
            "fid": q1,
            "from": (0, 0),
            "to": (0, 1)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Move,
            "fid": q2,
            "from": (0, 0),
            "to": (0, 1)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Move,
            "fid": q1,
            "from": (0, 1),
            "to": (0, 1)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Move,
            "fid": q1,
            "from": (0, 0),
            "to": (1, 1)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Move,
            "from": (0, 0),
            "to": (0, 1)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Move,
            "fid": q1,
            "to": (0, 1)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player": 10,
            "action": Action.Move,
            "fid": q1,
            "from": (0, 0)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], False)
        self.assertIsNotNone(result["reason"])
        self.assertIsNotNone(result["message"])

        action = {
            "player":10,
            "action":Action.Move,
            "fid":q1,
            "from":(0, 0),
            "to":(0, 1)
        }
        result = game.Act(action)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["fid"], q1)

    def testSkip(self):
        game = GameInstance(10, 11, GameSettings.GetSettings())

        preliminaryActions = [
            {
                "player": 10,
                "action": Action.Place,
                "figure": FigureType.Queen,
                "position": (0, 0)
            },
            {
                "player": 11,
                "action": Action.Place,
                "figure": FigureType.Queen,
                "position": (0, 1)
            },
            {
                "player": 10,
                "action": Action.Place,
                "figure": FigureType.Beetle,
                "position": (1, -1)
            },
            {
                "player": 11,
                "action": Action.Place,
                "figure": FigureType.Ant,
                "position": (0, 2)
            },
            {
                "player": 10,
                "action": Action.Place,
                "figure": FigureType.Beetle,
                "position": (-1, 0)
            },
            {
                "player": 11,
                "action": Action.Move,
                "fid": 4,
                "from": (0, 2),
                "to": (1, 1)
            },
            {
                "player": 10,
                "action": Action.Move,
                "fid": 3,
                "from": (1, -1),
                "to": (0, 0)
            },
            {
                "player": 11,
                "action": Action.Move,
                "fid": 4,
                "from": (1, 1),
                "to": (0, 2)
            },
            {
                "player": 10,
                "action": Action.Move,
                "fid": 5,
                "from": (-1, 0),
                "to": (0, 0)
            },
            {
                "player": 11,
                "action": Action.Move,
                "fid": 4,
                "from": (0, 2),
                "to": (1, 1)
            },
            {
                "player": 10,
                "action": Action.Move,
                "fid": 5,
                "from": (0, 0),
                "to": (0, 1)
            },
            {
                "player": 11,
                "action": Action.Move,
                "fid": 4,
                "from": (1, 1),
                "to": (-1, 1)
            },
            {
                "player": 10,
                "action": Action.Move,
                "fid": 3,
                "from": (0, 0),
                "to": (-1, 1)
            },
            {
                "player": 11,
                "action": Action.Skip
            },
        ]

        skipActions = [
            {
                "player": 10,
                "action": Action.Skip
            },
            {
                "player": 11,
                "action": Action.Skip
            }
        ]

        for i in range(0, len(preliminaryActions)):
            act = preliminaryActions[i]
            result = game.Act(act)
            self.assertEqual(result["result"], True, msg="error in iteration " + str(i))

            if i != len(preliminaryActions) - 2:
                for skip in skipActions:
                    result = game.Act(skip)
                    self.assertEqual(result["result"], False)

    def testConcede(self):
        game = GameInstance(10, 11, GameSettings.GetSettings())

        action1 = {
            "action":Action.Concede,
            "player":10
        }
        rv = game.Act(action1)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], True)
        self.assertEqual(rv["lost"][11], False)
        self.assertEqual(rv["ended"], True)

        action2 = {
            "action": Action.Concede,
            "player": 11
        }

        rv = game.Act(action2)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], True)
        self.assertEqual(rv["lost"][11], True)
        self.assertEqual(rv["ended"], True)

        game = GameInstance(10, 11, GameSettings.GetSettings())

        rv = game.Act(action2)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], False)
        self.assertEqual(rv["lost"][11], True)
        self.assertEqual(rv["ended"], True)

    def testForceEnd(self):
        game = GameInstance(10, 11, GameSettings.GetSettings())

        action = {
            "action": Action.ForceEnd,
            "player": 10
        }
        rv = game.Act(action)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], True)
        self.assertEqual(rv["lost"][11], False)
        self.assertEqual(rv["ended"], True)

        action = {
            "action": Action.ForceEnd,
            "player": 11
        }

        rv = game.Act(action)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], True)
        self.assertEqual(rv["lost"][11], True)
        self.assertEqual(rv["ended"], True)

        game = GameInstance(10, 11, GameSettings.GetSettings())

        rv = game.Act(action)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], False)
        self.assertEqual(rv["lost"][11], True)
        self.assertEqual(rv["ended"], True)

    def testSuggest(self):
        game = GameInstance(10, 11, GameSettings.GetSettings())

        action1 = {
            "action": Action.Suggest,
            "player": 10
        }
        rv = game.Act(action1)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], False)
        self.assertEqual(rv["lost"][11], False)
        self.assertEqual(rv["ended"], False)

        action2 = {
            "action": Action.Suggest,
            "player": 11
        }
        rv = game.Act(action2)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], True)
        self.assertEqual(rv["lost"][11], True)
        self.assertEqual(rv["ended"], True)

        game = GameInstance(10, 11, GameSettings.GetSettings())

        rv = game.Act(action2)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], False)
        self.assertEqual(rv["lost"][11], False)
        self.assertEqual(rv["ended"], False)

        rv = game.Act(action1)
        self.assertEqual(rv["result"], True)
        self.assertEqual(rv["lost"][10], True)
        self.assertEqual(rv["lost"][11], True)
        self.assertEqual(rv["ended"], True)


if __name__ == '__main__':
    unittest.main()
