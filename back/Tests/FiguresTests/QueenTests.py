import unittest
from Game.Utils.NegArray import NegArray
from Game.Settings.Figures.FigureTypes import FigureType
import Shared

class QueenTests(unittest.TestCase):
    def testAll(self):
        field = NegArray(2)
        queen = self.putQueen((0, 0), field)
        turns = queen.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        queen.ResetAvailTurns()

        self.putQueen((1, 0), field)
        turns = queen.AvailableTurns(field)
        ans = ((0, 1), (1, -1))
        self.assertEqual(len(turns), 2)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        queen.ResetAvailTurns()

        self.putQueen((-1, 0), field)
        turns = queen.AvailableTurns(field)
        ans = ((0, 1), (1, -1), (-1, 1), (0, -1))
        self.assertEqual(len(turns), 4)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        queen.ResetAvailTurns()

        self.putQueen((0, -1), field)
        turns = queen.AvailableTurns(field)
        ans = ((0, 1), (-1, 1))
        self.assertEqual(len(turns), 2)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        queen.ResetAvailTurns()

        self.putQueen((-1, 1), field)
        turns = queen.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        queen.ResetAvailTurns()

        self.putQueen((0, 1), field)
        self.putQueen((1, -1), field)
        turns = queen.AvailableTurns(field)
        self.assertEqual(len(turns), 0)

        queen = field.Get((-1, 1))[0]
        turns = queen.AvailableTurns(field)
        ans = ((-2, 1), (-1, 2))
        self.assertEqual(len(turns), 2)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))


    def putQueen(self, pos, field):
        q = FigureType.Queen.GetFigure(0, pos)
        field.Put([q], pos)
        return q

if __name__ == '__main__':
    unittest.main()