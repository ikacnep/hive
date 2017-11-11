#TODO: requires more tests

import unittest
from Game.Settings.GameSettings import GameSettings
from Game.GameInstance import GameInstance
from Game.Settings.Figures.FigureTypes import FigureType
from Game.Utils.Action import Action
from Game.Utils.Exceptions import *

class GameInstanceTests(unittest.TestCase):
    def testPlacement(self):
        game = GameInstance(10, 11, GameSettings.GetSettings())
        placeAction = {
            "action":Action.Place,
            "figure":FigureType.Ant,
            "player":11,
            "position":(0, 0)
        }
        actions = game.GetActions()

        rv = game.Act(placeAction)
        self.assertFalse(rv["result"])
        self.assertEqual(rv["reason"], ActionImpossible)
        self.assertIsNotNone(rv["message"])

        self.assertEqual(len(actions["placements"][10][0]), 5)
        self.assertEqual(actions["nextPlayer"], 10)
        placeAction["player"] = 10
        rv = game.Act(placeAction)
        self.assertTrue(rv["result"])
        self.assertEqual(rv["turn"], 1)
        self.assertEqual(rv["nextPlayer"], 11)
        actions = rv["actions"]

        self.assertEqual(len(actions["placements"][11][0]), 5)
        self.assertEqual(len(actions["placements"][11][1]), 6)

        placeAction["position"] = (0, 1)
        rv = game.Act(placeAction)
        self.assertFalse(rv["result"])
        self.assertEqual(rv["reason"], ActionImpossible)
        self.assertIsNotNone(rv["message"])

        placeAction["player"] = 11
        rv = game.Act(placeAction)
        self.assertEqual(rv["turn"], 2)
        self.assertEqual(rv["nextPlayer"], 10)

    def testMovement(self):
        game = GameInstance(10, 11, GameSettings.GetSettings(pillbug=True))

        placeAction = {
            "action": Action.Place,
            "figure": FigureType.Queen,
            "player": 10,
            "position": (0, 0)
        }

        rv = game.Act(placeAction)
        q1 = rv["fid"]
        placeAction["player"] = 11
        placeAction["position"] = (0, 1)
        rv = game.Act(placeAction)
        q2 = rv["fid"]
        actions = rv["actions"]
        self.assertEqual(len(actions["turns"][10]), 1)
        self.assertEqual(len(actions["turns"][10][q1]), 2)

        placeAction["player"] = 10
        placeAction["position"] = (0, -1)
        placeAction["figure"] = FigureType.Ant
        rv = game.Act(placeAction)
        ant1 = rv["fid"]
        actions = rv["actions"]
        self.assertEqual(len(actions["turns"][11]), 1)
        self.assertEqual(len(actions["turns"][11][q2]), 2)

        placeAction["player"] = 11
        placeAction["position"] = (0, 2)
        rv = game.Act(placeAction)
        ant2 = rv["fid"]
        actions = rv["actions"]
        self.assertEqual(len(actions["turns"][10]), 1)
        self.assertEqual(len(actions["turns"][10][ant1]), 9)

        moveAction = {
            "action":Action.Move,
            "player":10,
            "fid":ant1,
            "from":(0, -1),
            "to":(0, -2)
        }
        rv = game.Act(moveAction)
        self.assertFalse(rv["result"])
        self.assertEqual(rv["reason"], ActionImpossible)
        self.assertIsNotNone(rv["message"])

        moveAction["fid"] = 15
        rv = game.Act(moveAction)
        self.assertFalse(rv["result"])
        self.assertEqual(rv["reason"], ActionImpossible)
        self.assertIsNotNone(rv["message"])

        moveAction["fid"] = ant2
        moveAction["from"] = (0, 2)
        moveAction["to"] = (0, -2)
        moveAction["player"] = 11
        rv = game.Act(moveAction)
        self.assertFalse(rv["result"])
        self.assertEqual(rv["reason"], ActionImpossible)
        self.assertIsNotNone(rv["message"])

        moveAction["fid"] = ant1
        moveAction["from"] = (0, -1)
        moveAction["to"] = (0, 3)
        moveAction["player"] = 10
        rv = game.Act(moveAction)
        self.assertTrue(rv["result"])
        self.assertEqual(rv["turn"], 5)
        self.assertEqual(rv["nextPlayer"], 11)

if __name__ == '__main__':
    unittest.main()