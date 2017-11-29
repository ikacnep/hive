import unittest
from ...Game.Utils.NegArray import NegArray
from ...Game.Settings.Figures.FigureTypes import FigureType
from ... import Shared

class AntTests(unittest.TestCase):
    def testAdequate(self):
        field = NegArray(2)
        ant = self.putAnt((0, 0), field)
        turns = ant.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        ant.ResetAvailTurns()

        self.putAnt((1, 0), field)
        turns = ant.AvailableTurns(field)
        ans = Shared.Except(Shared.CellsNearby((1, 0)), [(0, 0)])
        self.assertEqual(len(turns), 5)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        ant.ResetAvailTurns()

        self.putAnt((0, 1), field)
        turns = ant.AvailableTurns(field)
        ans = Shared.Except(Shared.Union(ans, Shared.CellsNearby((0, 1))),  [(0, 0), (1,0), (0,1)])
        self.assertEqual(len(turns), 7)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        ant.ResetAvailTurns()

        self.putAnt((-1, 1), field)
        turns = ant.AvailableTurns(field)
        ans = Shared.Except(Shared.Union(ans, Shared.CellsNearby((-1, 1))), [(0, 0), (1, 0), (0, 1), (-1, 1)])
        self.assertEqual(len(turns), 9)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        ant.ResetAvailTurns()

        self.putAnt((0, -1), field)
        turns = ant.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        ant.ResetAvailTurns()

    def testPassage(self):
        field = NegArray(2)
        ant = self.putAnt((0, 0), field)
        turns = ant.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        ant.ResetAvailTurns()

        self.putAnt((1, 0), field)
        self.putAnt((-1, 1), field)
        turns = ant.AvailableTurns(field)
        ans = Shared.Except(Shared.Union(Shared.CellsNearby((1, 0)), Shared.CellsNearby((-1, 1))), [(0, 0)])
        self.assertEqual(len(turns), 9)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        ant.ResetAvailTurns()

    def testComplex(self):
        field = NegArray(2)
        ant = self.putAnt((0, 0), field)
        self.putAnt((-1, 1), field)
        self.putAnt((-2, 2), field)
        self.putAnt((-1, 0), field)
        self.putAnt((-2, 0), field)
        self.putAnt((-3, 1), field)

        turns = ant.AvailableTurns(field)
        ans = [(0, 1), (-1, 2), (-2, 3), (-3, 3), (-3, 2), (-4, 2), (-4, 1), (-3, 0), (-2, -1), (-1, -1), (0, -1)]
        self.assertEqual(len(turns),11)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        ant.ResetAvailTurns()


    def putAnt(self, pos, field):
        q = FigureType.Ant.GetFigure(0, pos)
        field.Put([q], pos)
        return q

if __name__ == '__main__':
    unittest.main()
