import unittest
from Game.Settings.GameSettings import GameSettings
from Game.GameState import GameState
from Game.Settings.Figures.FigureTypes import FigureType
import Shared

class PillbugTests(unittest.TestCase):
    def testAll(self):
        field = GameState(GameSettings.GetSettings())
        pillbug = self.putPillbug((0, 0), field)
        turns = pillbug.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        pillbug.ResetAvailTurns()

        self.putPillbug((1, 0), field)
        turns = pillbug.AvailableTurns(field)
        ans = ((0, 1), (1, -1), ((1,0),(0,1)), ((1,0),(1,-1)), ((1,0),(-1,1)), ((1,0),(0,-1)), ((1,0),(-1,0)))
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        pillbug.ResetAvailTurns()

        self.putPillbug((-1, 0), field)
        turns = pillbug.AvailableTurns(field)
        ans = ((0, 1), (1, -1), (-1, 1), (0, -1), ((1,0),(0,1)), ((1,0),(1,-1)), ((1,0),(-1,1)), ((1,0),(0,-1)), ((-1,0),(0,1)), ((-1,0),(1,-1)), ((-1,0),(-1,1)), ((-1,0),(0,-1)))
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        pillbug.ResetAvailTurns()

        self.putPillbug((0, -1), field)
        turns = pillbug.AvailableTurns(field)
        ans = ((0, 1), (-1, 1), ((1,0),(0,1)), ((1,0),(1,-1)), ((1,0),(-1,1)), ((-1,0),(0,1)), ((-1,0),(1,-1)), ((-1,0),(-1,1)), ((0,-1),(0,1)), ((0,-1),(1,-1)), ((0,-1),(-1,1)))
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        pillbug.ResetAvailTurns()

        self.putPillbug((-1, 1), field)
        turns = pillbug.AvailableTurns(field)
        ans = (((1, 0), (0, 1)), ((1, 0), (1, -1)), ((-1, 0), (0, 1)), ((-1, 0), (1, -1)), ((0, -1), (0, 1)), ((0, -1), (1, -1)), ((-1, 1), (0, 1)), ((-1, 1), (1, -1)))
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        pillbug.ResetAvailTurns()

        self.putPillbug((0, 1), field)
        self.putPillbug((1, -1), field)
        turns = pillbug.AvailableTurns(field)
        self.assertEqual(len(turns), 0)

    def putPillbug(self, pos, field):
        q = FigureType.Pillbug.GetFigure(0, pos)
        field.Put(q)
        return q

if __name__ == '__main__':
    unittest.main()