import unittest
from Game.Settings.GameSettings import GameSettings
from Game.GameState import GameState
from Game.Utils.Exceptions import *
from Game.Settings.Figures.FigureTypes import FigureType
from Shared import *

class GameStateTests(unittest.TestCase):
    def testPlacement(self):
        game = GameState(GameSettings.GetSettings())
        with self.assertRaises(ActionImpossible):
            game.Place(1, (FigureType.Ant, (0, 0)))
        self.assertEqual(game.turn, 0)

        self.assertEqual(len(game.availPlacements[0]), 11)
        game.Place(0, (FigureType.Ant, (0, 0)))
        self.assertEqual(game.turn, 1)
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ant, (0, 1)))

        self.assertEqual(len(game.availPlacements[1]), 66)
        game.Place(1, (FigureType.Ant, (0, 1)))
        self.assertEqual(game.turn, 2)

        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ant, (1, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ant, (-1, 1)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ant, (0, 2)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ant, (0, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ant, (0, 1)))

        self.assertEqual(len(game.availPlacements[0]), 30)
        game.Place(0, (FigureType.Ant, (-1, 0)))
        self.assertEqual(game.turn, 3)

        self.assertEqual(len(game.availPlacements[1]), 30)
        game.Place(1, (FigureType.Ant, (-1, 2)))
        self.assertEqual(game.turn, 4)

        self.assertEqual(len(game.availPlacements[0]), 45)
        game.Place(0, (FigureType.Ant, (-2, 1)))
        self.assertEqual(game.turn, 5)

        with self.assertRaises(ActionImpossible):
            game.Place(1, (FigureType.Ant, (-2, 2)))

        self.assertEqual(len(game.availPlacements[1]), 36)
        game.Place(1, (FigureType.Ant, (0, 2)))
        self.assertEqual(game.turn, 6)

        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Beetle, (0, -1)))

        self.assertEqual(len(game.availPlacements[0]), 6)
        game.Place(0, (FigureType.Queen, (0, -1)))
        self.assertEqual(game.turn, 7)

        with self.assertRaises(ActionImpossible):
            game.Place(1, (FigureType.Beetle, (0, 2)))

        self.assertEqual(len(game.availPlacements[1]), 5)
        game.Place(1, (FigureType.Queen, (0, 3)))
        self.assertEqual(game.turn, 8)

        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ant, (0, -2)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Queen, (0, -2)))

        self.assertEqual(len(game.availPlacements[0]), 49)
        game.Place(0, (FigureType.Beetle, (0, -2)))
        self.assertEqual(game.turn, 9)

    def testLockAndSkip(self):
        game = GameState(GameSettings.GetSettings())

        game.Place(0, (FigureType.Ant, (0, 0)))
        game.Place(1, (FigureType.Ant, (0, 1)))

        game.Put(FigureType.Ant.GetFigure(1, (-1, 2)))
        game.Put(FigureType.Ant.GetFigure(1, (-2, 1)))
        game.Put(FigureType.Ant.GetFigure(1, (-1, -1)))
        game.Put(FigureType.Ant.GetFigure(1, (1, -2)))
        game.Put(FigureType.Ant.GetFigure(1, (2, -1)))
        game.Put(FigureType.Ant.GetFigure(1, (1, -1)))

        game.RefreshPossibilities()

        self.assertEqual(len(game.availPlacements[0]), 0)

        self.assertTrue(game.Skip(0))
        self.assertEqual(game.turn, 3)

    def testMovement(self):
        game = GameState(GameSettings.GetSettings(pillbug=True))

        q1 = game.Place(0, (FigureType.Queen, (0, 0)))
        q2 = game.Place(1, (FigureType.Queen, (0, 1)))

        self.assertEqual(len(game.availActions[0]), 1)
        self.assertEqual(len(game.availActions[0][q1]), 2)
        ant1 = game.Place(0, (FigureType.Ant, (0, -1)))

        self.assertEqual(len(game.availActions[1]), 1)
        self.assertEqual(len(game.availActions[1][q2]), 2)
        ant2 = game.Place(1, (FigureType.Ant, (0, 2)))

        self.assertEqual(len(game.availActions[0]), 1)
        self.assertEqual(len(game.availActions[0][ant1]), 9)

        with self.assertRaises(ActionImpossible):
            game.Move(0, ant1, (0, -1), (0, -2))
        with self.assertRaises(ActionImpossible):
            game.Move(0, ant1, (0, -1), (0, 0))
        with self.assertRaises(ActionImpossible):
            game.Move(0, ant1, (0, -1), (0, 2))
        with self.assertRaises(ActionImpossible):
            game.Move(0, 15, (0, -1), (0, -2))
        with self.assertRaises(ActionImpossible):
            game.Move(0, q1, (0, -1), (0, -2))
        with self.assertRaises(ActionImpossible):
            game.Move(0, ant2, (0, 2), (0, -2))
        with self.assertRaises(ActionImpossible):
            game.Move(1, ant2, (0, 2), (0, -2))

        game.Move(0, ant1, (0, -1), (0, 3))
        self.assertEqual(game.turn, 5)

        self.assertEqual(len(game.availActions[1]), 0)
        ant22 = game.Place(1, (FigureType.Ant, (-1, 2)))

        self.assertEqual(len(game.availActions[0]), 2)
        ant12 = game.Place(0, (FigureType.Ant, (0, -1)))

        self.assertEqual(len(game.availActions[1]), 1)
        self.assertEqual(len(game.availActions[1][ant22]), 13)

        with self.assertRaises(ActionImpossible):
            game.Move(1, ant2, (0, 2), (0, -2))
        with self.assertRaises(ActionImpossible):
            game.Move(1, ant22, (0, 2), (0, -2))
        with self.assertRaises(ActionImpossible):
            game.Move(0, ant22, (-1, 2), (0, -2))
        with self.assertRaises(ActionImpossible):
            game.Move(1, ant12, (0, -1), (0, 4))

        game.Move(1, ant22, (-1, 2), (0, 4))

        self.assertEqual(len(game.availActions[0]), 1)
        self.assertEqual(len(game.availActions[0][ant12]), 13)
        pill = game.Place(0, (FigureType.Pillbug, (1, -1)))
        g2 = game.Place(1, (FigureType.Grasshopper, (1, 1)))

        g1 = game.Place(0, (FigureType.Grasshopper, (0, -2)))
        game.Move(1, ant22, (0, 4), (2, -2))

        self.assertEqual(len(game.availActions[0]), 2)
        with self.assertRaises(ActionImpossible):
            game.Move(0, pill, (1, -1), (1, 0))
        with self.assertRaises(ActionImpossible):
            game.Move(0, pill, (0, 0), (1, 0))
        with self.assertRaises(ActionImpossible):
            game.Move(0, pill, (2, -2), (1, 0))

        g1 = game.Place(0, (FigureType.Grasshopper, (0, -3)))
        g2 = game.Place(1, (FigureType.Grasshopper, (2, 1)))

        self.assertEqual(len(game.availActions[0]), 3)
        self.assertEqual(game.Move(0, pill, (2, -2), (1, 0)), ant22)

    def testWinCondition(self):
        game = GameState(GameSettings.GetSettings())
        game.Place(0, (FigureType.Queen, (0, 0)))
        game.Place(1, (FigureType.Queen, (0, 1)))

        af = FigureType.Ant.GetFigure(0, (-1, 1))
        game.Put(af)
        game.Put(FigureType.Ant.GetFigure(0, (-1, 0)))
        af2 = FigureType.Ant.GetFigure(0, (0, -1))
        game.Put(af2)
        game.Put(FigureType.Ant.GetFigure(0, (1, -1)))
        game.Put(FigureType.Ant.GetFigure(0, (1, 0)))

        game.RefreshPossibilities()
        self.assertTrue(game.gameEnded)
        self.assertTrue(game.hasLost[0])
        self.assertFalse(game.hasLost[1])

        game.Put(FigureType.Ant.GetFigure(0, (-1, 2)))
        game.Put(FigureType.Ant.GetFigure(0, (0, 2)))
        game.Put(FigureType.Ant.GetFigure(0, (1, 1)))

        game.RefreshPossibilities()
        self.assertTrue(game.gameEnded)
        self.assertTrue(game.hasLost[0])
        self.assertTrue(game.hasLost[1])

        game.Remove((-1, 1))
        game.figures.pop(af.id)
        game.RefreshPossibilities()
        self.assertFalse(game.gameEnded)
        self.assertFalse(game.hasLost[0])
        self.assertFalse(game.hasLost[1])

        game.Put(FigureType.Ant.GetFigure(0, (-1, 1)))
        game.Remove((0, -1))
        game.figures.pop(af2.id)
        game.RefreshPossibilities()
        self.assertTrue(game.gameEnded)
        self.assertFalse(game.hasLost[0])
        self.assertTrue(game.hasLost[1])


    def testSettings(self):
        game = GameState(GameSettings.GetSettings())
        self.assertEqual(len(game.availPlacements[0]), 11)
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Mosquito, (0, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ladybug, (0, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Pillbug, (0, 0)))

        game.Place(0, (FigureType.Queen, (0, 0)))
        self.assertEqual(game.turn, 1)

        game = GameState(GameSettings.GetSettings(tourney=True))
        self.assertEqual(len(game.availPlacements[0]), 10)
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Mosquito, (0, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ladybug, (0, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Pillbug, (0, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Queen, (0, 0)))

        self.assertEqual(game.turn, 0)
        game.Place(0, (FigureType.Ant, (0, 0)))
        self.assertEqual(game.turn, 1)

        game = GameState(GameSettings.GetSettings(mosquito=True))
        self.assertEqual(len(game.availPlacements[0]), 12)
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ladybug, (0, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Pillbug, (0, 0)))

        game.Place(0, (FigureType.Mosquito, (0, 0)))
        self.assertEqual(game.turn, 1)

        game = GameState(GameSettings.GetSettings(ladybug=True))
        self.assertEqual(len(game.availPlacements[0]), 12)
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Mosquito, (0, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Pillbug, (0, 0)))

        game.Place(0, (FigureType.Ladybug, (0, 0)))
        self.assertEqual(game.turn, 1)

        game = GameState(GameSettings.GetSettings(pillbug=True))
        self.assertEqual(len(game.availPlacements[0]), 12)
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Mosquito, (0, 0)))
        with self.assertRaises(ActionImpossible):
            game.Place(0, (FigureType.Ladybug, (0, 0)))

        game.Place(0, (FigureType.Pillbug, (0, 0)))
        self.assertEqual(game.turn, 1)

        game = GameState(GameSettings.GetSettings(mosquito=True, ladybug=True, pillbug=True))
        self.assertEqual(len(game.availPlacements[0]), 14)
        game.Place(0, (FigureType.Mosquito, (0, 0)))
        game.Place(1, (FigureType.Ladybug, (1, 0)))
        game.Place(0, (FigureType.Pillbug, (0, -1)))
        self.assertEqual(game.turn, 3)

if __name__ == '__main__':
    unittest.main()