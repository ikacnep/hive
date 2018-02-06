import unittest

from ... import Shared
from ...Game.Settings.Figures.FigureTypes import FigureType
from ...Game.Utils.NegArray import NegArray


class BeetleTests(unittest.TestCase):
    def testAll(self):
        field = NegArray(2)
        beetle = self.putBeetle((0, 0), field)
        turns = beetle.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        beetle.ResetAvailTurns()

        self.putBeetle((1, 0), field)
        turns = beetle.AvailableTurns(field)
        ans = ((0, 1), (1, -1), (1, 0))
        self.assertEqual(len(turns), 3)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        beetle.ResetAvailTurns()

        self.putBeetle((-1, 0), field)
        turns = beetle.AvailableTurns(field)
        ans = ((0, 1), (1, -1), (-1, 1), (0, -1), (1, 0), (-1, 0))
        self.assertEqual(len(turns), 6)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        beetle.ResetAvailTurns()

        self.putBeetle((0, -1), field)
        turns = beetle.AvailableTurns(field)
        ans = ((0, 1), (-1, 1), (1, 0), (-1, 0), (0, -1))
        self.assertEqual(len(turns), 5)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        beetle.ResetAvailTurns()

        self.putBeetle((-1, 1), field)
        turns = beetle.AvailableTurns(field)
        ans = ((-1, 1), (1, 0), (-1, 0), (0, -1))
        self.assertEqual(len(turns), 4)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        beetle.ResetAvailTurns()

        self.putBeetle((0, 1), field)
        self.putBeetle((1, -1), field)
        ans = ((-1, 1), (1, 0), (-1, 0), (0, -1), (0, 1), (-1, 1))
        turns = beetle.AvailableTurns(field)
        self.assertEqual(len(turns), 6)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        beetle.ResetAvailTurns()

        beetle = field.Get((-1, 1))[0]
        turns = beetle.AvailableTurns(field)
        ans = ((-2, 1), (-1, 2), (0, 0), (0, 1), (-1, 0))
        self.assertEqual(len(turns), 5)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))

    def testWell(self):
        field = NegArray(2)
        self.putBeetle((1, 0), field)
        self.putBeetle((-1, 0), field)
        self.putBeetle((0, -1), field)
        self.putBeetle((1, -1), field)
        self.putBeetle((0, 1), field)
        beetle = self.putBeetle((-1, 1), field)

        turns = beetle.AvailableTurns(field)
        ans = ((-2, 1), (-1, 2), (0, 1), (-1, 0))
        self.assertEqual(len(turns), 4)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))

        beetle = self.addBeetle((-1, 1), field)
        turns = beetle.AvailableTurns(field)
        ans = ((-2, 1), (-1, 2), (0, 1), (-1, 0), (0, 0))
        self.assertEqual(len(turns), 5)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))

    def testMoveDownDoesNotSplit(self):
        field = NegArray(2)

        self.putBeetle((0, 0), field)
        self.putBeetle((1, 0), field)
        beetle = self.addBeetle((0, 0), field)

        ans = ((0, -1), (1, -1), (1, 0), (0, 1), (1, -1), (-1, 0))
        turns = beetle.AvailableTurns(field)

        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))

    @staticmethod
    def putBeetle(pos, field):
        q = FigureType.Beetle.GetFigure(0, pos)
        field.Put([q], pos)
        return q

    @staticmethod
    def addBeetle(pos, field):
        q = FigureType.Beetle.GetFigure(0, pos)
        prev = field.Get(pos)
        if prev is None:
            field.Put([q], pos)
        else:
            prev.insert(0, q)

        return q


if __name__ == '__main__':
    unittest.main()
