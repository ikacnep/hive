import unittest

from ... import Shared
from ...Game.Settings.Figures.FigureTypes import FigureType
from ...Game.Utils.NegArray import NegArray


class LadybugTests(unittest.TestCase):
    def testAll(self):
        field = NegArray(2)
        ladybug = self.putLadybug((0, 0), field)
        turns = ladybug.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        ladybug.ResetAvailTurns()

        self.putLadybug((1, 0), field)
        turns = ladybug.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        ladybug.ResetAvailTurns()

        self.putLadybug((0, 1), field)
        turns = ladybug.AvailableTurns(field)
        ans = Shared.Except(Shared.Union(Shared.CellsNearby((0, 1)), Shared.CellsNearby((1, 0))),
                            [(0, 0), (0, 1), (1, 0)])
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        ladybug.ResetAvailTurns()

        self.putLadybug((1, -1), field)
        ans = Shared.Union(ans, Shared.CellsNearby((1, -1)))
        self.putLadybug((0, -1), field)
        ans = Shared.Union(ans, Shared.CellsNearby((0, -1)))
        self.putLadybug((-1, 0), field)
        ans = Shared.Union(ans, Shared.CellsNearby((-1, 0)))
        self.putLadybug((-1, 1), field)
        ans = Shared.Union(ans, Shared.CellsNearby((-1, 1)))
        ans = Shared.Except(Shared.Except(ans, Shared.CellsNearby((0, 0))), [(0, 0)])

        turns = ladybug.AvailableTurns(field)
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        ladybug.ResetAvailTurns()

    @staticmethod
    def putLadybug(pos, field):
        q = FigureType.Ladybug.GetFigure(0, pos)
        field.Put([q], pos)
        return q


if __name__ == '__main__':
    unittest.main()
