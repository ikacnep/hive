import unittest

from ... import Shared
from ...Game.GameState import GameState
from ...Game.Settings.Figures.FigureTypes import FigureType
from ...Game.Settings.GameSettings import GameSettings
from ...Game.Utils.NegArray import NegArray


# Beware! Tests are copied from all other figures!
class MosquitoTests(unittest.TestCase):
    def testPillbug(self):
        field = GameState(GameSettings.GetSettings())
        pillbug = self.putMosquitoNoList((0, 0), field)
        turns = pillbug.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        pillbug.ResetAvailTurns()

        self.putPillbug((1, 0), field)
        turns = pillbug.AvailableTurns(field)
        ans = (
            (0, 1), (1, -1), ((1, 0), (0, 1)), ((1, 0), (1, -1)), ((1, 0), (-1, 1)), ((1, 0), (0, -1)),
            ((1, 0), (-1, 0))
        )
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        pillbug.ResetAvailTurns()

        self.putPillbug((-1, 0), field)
        turns = pillbug.AvailableTurns(field)
        ans = (
            (0, 1), (1, -1), (-1, 1), (0, -1), ((1, 0), (0, 1)), ((1, 0), (1, -1)), ((1, 0), (-1, 1)),
            ((1, 0), (0, -1)), ((-1, 0), (0, 1)), ((-1, 0), (1, -1)), ((-1, 0), (-1, 1)), ((-1, 0), (0, -1))
        )
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        pillbug.ResetAvailTurns()

        self.putPillbug((0, -1), field)
        turns = pillbug.AvailableTurns(field)
        ans = (
            (0, 1), (-1, 1), ((1, 0), (0, 1)), ((1, 0), (1, -1)), ((1, 0), (-1, 1)), ((-1, 0), (0, 1)),
            ((-1, 0), (1, -1)), ((-1, 0), (-1, 1)), ((0, -1), (0, 1)), ((0, -1), (1, -1)), ((0, -1), (-1, 1))
        )
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        pillbug.ResetAvailTurns()

        self.putPillbug((-1, 1), field)
        turns = pillbug.AvailableTurns(field)
        ans = (((1, 0), (0, 1)), ((1, 0), (1, -1)), ((-1, 0), (0, 1)), ((-1, 0), (1, -1)), ((0, -1), (0, 1)),
               ((0, -1), (1, -1)), ((-1, 1), (0, 1)), ((-1, 1), (1, -1)))
        self.assertEqual(len(turns), len(ans))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        pillbug.ResetAvailTurns()

        self.putPillbug((0, 1), field)
        self.putPillbug((1, -1), field)
        turns = pillbug.AvailableTurns(field)
        self.assertEqual(len(turns), 0)

    def testAntAdequate(self):
        field = NegArray(2)
        ant = self.putMosquito((0, 0), field)
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
        ans = Shared.Except(Shared.Union(ans, Shared.CellsNearby((0, 1))), [(0, 0), (1, 0), (0, 1)])
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

    def testAntPassage(self):
        field = NegArray(2)
        ant = self.putMosquito((0, 0), field)
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

    def testAntComplex(self):
        field = NegArray(2)
        ant = self.putMosquito((0, 0), field)
        self.putAnt((-1, 1), field)
        self.putAnt((-2, 2), field)
        self.putAnt((-1, 0), field)
        self.putAnt((-2, 0), field)
        self.putAnt((-3, 1), field)

        turns = ant.AvailableTurns(field)
        ans = [(0, 1), (-1, 2), (-2, 3), (-3, 3), (-3, 2), (-4, 2), (-4, 1), (-3, 0), (-2, -1), (-1, -1), (0, -1)]
        self.assertEqual(len(turns), 11)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        ant.ResetAvailTurns()

    def testBeetleAll(self):
        field = NegArray(2)
        beetle = self.putMosquito((0, 0), field)
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

    def testBeetleWell(self):
        field = NegArray(2)
        self.putBeetle((1, 0), field)
        self.putBeetle((-1, 0), field)
        self.putBeetle((0, -1), field)
        self.putBeetle((1, -1), field)
        self.putBeetle((0, 1), field)
        beetle = self.putMosquito((-1, 1), field)

        turns = beetle.AvailableTurns(field)
        ans = ((-2, 1), (-1, 2), (0, 1), (-1, 0))
        self.assertEqual(len(turns), 4)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))

        beetle = self.addMosquito((-1, 1), field)
        turns = beetle.AvailableTurns(field)
        ans = ((-2, 1), (-1, 2), (0, 1), (-1, 0), (0, 0))
        self.assertEqual(len(turns), 5)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))

    def testMosquitBeetle(self):
        field = NegArray(2)
        self.putMosquito((1, 0), field)
        self.putMosquito((-1, 0), field)
        self.putMosquito((0, -1), field)
        self.putMosquito((1, -1), field)
        self.putMosquito((0, 1), field)
        self.putMosquito((-1, 1), field)

        beetle = self.addMosquito((-1, 1), field)
        turns = beetle.AvailableTurns(field)
        ans = ((-2, 1), (-1, 2), (0, 1), (-1, 0), (0, 0))
        self.assertEqual(len(turns), 5)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))

    def testGrasshopperZeroPlus(self):
        field = NegArray(2)
        grasshopper = self.putMosquito((0, 0), field)
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

    def testLadybugAll(self):
        field = NegArray(2)
        ladybug = self.putMosquito((0, 0), field)
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

    def testQueenAll(self):
        field = NegArray(2)
        queen = self.putMosquito((0, 0), field)
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

    def testSpiderAll(self):
        field = NegArray(2)
        spider = self.putMosquito((0, 0), field)
        turns = spider.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        spider.ResetAvailTurns()

        self.putSpider((1, 0), field)
        turns = spider.AvailableTurns(field)
        ans = [(2, 0)]
        self.assertEqual(len(turns), 1)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        spider.ResetAvailTurns()

        self.putSpider((0, 1), field)
        turns = spider.AvailableTurns(field)
        ans = [(2, 0), (0, 2)]
        self.assertEqual(len(turns), 2)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        spider.ResetAvailTurns()

        self.putSpider((-1, 0), field)
        turns = spider.AvailableTurns(field)
        ans = [(-2, 0), (2, 0)]
        self.assertEqual(len(turns), 2)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        spider.ResetAvailTurns()

    def testSpiderComplex(self):
        field = NegArray(2)
        spider = self.putMosquito((0, 0), field)

        self.putSpider((0, -1), field)
        self.putSpider((-1, 0), field)
        self.putSpider((-2, 1), field)
        self.putSpider((-2, 2), field)
        self.putSpider((-1, 2), field)
        self.putSpider((0, 2), field)
        self.putSpider((1, 1), field)
        self.putSpider((2, 0), field)
        self.putSpider((2, -1), field)
        self.putSpider((1, -1), field)

        turns = spider.AvailableTurns(field)
        ans = [(-1, 1), (1, 0)]
        self.assertEqual(len(turns), 2)
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect(ans, turns), ans))
        spider.ResetAvailTurns()

        self.putSpider((1, 0), field)
        turns = spider.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        spider.ResetAvailTurns()

    @staticmethod
    def putSpider(pos, field):
        q = FigureType.Spider.GetFigure(0, pos)
        field.Put([q], pos)
        return q

    @staticmethod
    def putQueen(pos, field):
        q = FigureType.Queen.GetFigure(0, pos)
        field.Put([q], pos)
        return q

    @staticmethod
    def putLadybug(pos, field):
        q = FigureType.Ladybug.GetFigure(0, pos)
        field.Put([q], pos)
        return q

    @staticmethod
    def putGrasshopper(pos, field):
        q = FigureType.Grasshopper.GetFigure(0, pos)
        field.Put([q], pos)
        return q

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

    @staticmethod
    def putAnt(pos, field):
        q = FigureType.Ant.GetFigure(0, pos)
        field.Put([q], pos)
        return q

    @staticmethod
    def putPillbug(pos, field):
        q = FigureType.Pillbug.GetFigure(0, pos)
        field.Put(q)
        return q

    @staticmethod
    def putMosquitoNoList(pos, field):
        q = FigureType.Mosquito.GetFigure(0, pos)
        field.Put(q)
        return q

    @staticmethod
    def putMosquito(pos, field):
        q = FigureType.Mosquito.GetFigure(0, pos)
        field.Put([q], pos)
        return q

    @staticmethod
    def addMosquito(pos, field):
        q = FigureType.Mosquito.GetFigure(0, pos)
        prev = field.Get(pos)
        if prev is None:
            field.Put([q], pos)
        else:
            prev.insert(0, q)

        return q


if __name__ == '__main__':
    unittest.main()
