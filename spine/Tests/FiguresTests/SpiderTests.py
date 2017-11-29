import unittest
from ...Game.Utils.NegArray import NegArray
from ...Game.Settings.Figures.FigureTypes import FigureType
from ... import Shared

class SpiderTests(unittest.TestCase):
    def testAll(self):
        field = NegArray(2)
        spider = self.putSpider((0, 0), field)
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

    def testComplex(self):
        field = NegArray(2)
        spider = self.putSpider((0, 0), field)

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


    def putSpider(self, pos, field):
        q = FigureType.Spider.GetFigure(0, pos)
        field.Put([q], pos)
        return q

if __name__ == '__main__':
    unittest.main()
