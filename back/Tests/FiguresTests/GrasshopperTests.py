import unittest
from Game.Utils.NegArray import NegArray
from Game.Settings.Figures.FigureTypes import FigureType
import Shared

class GrasshopperTests(unittest.TestCase):
    def testZeroPlus(self):
        field = NegArray(2)
        grasshopper = self.putGrasshopper((0, 0), field)
        turns = grasshopper.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((1, 0), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(2, 0)]
        self.assertEqual(len(turns), 1)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((0, 1), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(2, 0), (0, 2)]
        self.assertEqual(len(turns), 2)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((-1, 1), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(2, 0), (0, 2), (-2, 2)]
        self.assertEqual(len(turns), 3)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((2, 0), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(3, 0), (0, 2), (-2, 2)]
        self.assertEqual(len(turns), 3)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((0, 2), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(3, 0), (0, 3), (-2, 2)]
        self.assertEqual(len(turns), 3)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((-2, 2), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(3, 0), (0, 3), (-3, 3)]
        self.assertEqual(len(turns), 3)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((-1, 0), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(3, 0), (0, 3), (-3, 3), (-2, 0)]
        self.assertEqual(len(turns), 4)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((0, -2), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(3, 0), (0, 3), (-3, 3), (-2, 0)]
        self.assertEqual(len(turns), 4)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((0, -1), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(3, 0), (0, 3), (-3, 3), (-2, 0), (0, -3)]
        self.assertEqual(len(turns), 5)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

        self.putGrasshopper((1, -1), field)
        turns = grasshopper.AvailableTurns(field)
        ans = [(3, 0), (0, 3), (-3, 3), (-2, 0), (0, -3), (2, -2)]
        self.assertEqual(len(turns), 6)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        grasshopper.ResetAvailTurns()

    def putGrasshopper(self, pos, field):
        q = FigureType.Grasshopper.GetFigure(0, pos)
        field.Put([q], pos)
        return q

if __name__ == '__main__':
    unittest.main()