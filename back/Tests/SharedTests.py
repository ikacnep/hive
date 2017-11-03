import unittest
import Shared

class SharedTests(unittest.TestCase):
    def testEquality(self):
        self.assertTrue(Shared.ReallyEqual(None, None))
        self.assertFalse(Shared.ReallyEqual(None, ()))
        self.assertFalse(Shared.ReallyEqual((), None))
        self.assertTrue(Shared.ReallyEqual((1,2,3), (1,2,3)))
        self.assertFalse(Shared.ReallyEqual((1, 2, 3), (1, 2, 3, 4)))
        self.assertFalse(Shared.ReallyEqual((1, 2, 3, 4), (1, 2, 3)))
        self.assertFalse(Shared.ReallyEqual((1, 2, 3), (1, -2, 3)))
        self.assertFalse(Shared.ReallyEqual((1, 2, 3), (1, (2, 5), 3)))
        self.assertTrue(Shared.ReallyEqual((1, (2, 4), 3), (1, (2, 4), 3)))
        self.assertTrue(Shared.ReallyEqual((1, (2, 3, ()), 3), (1, (2, 3, ()), 3)))

    def testIntersection(self):
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect((), ()), ()))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect((), (1, 2, 3)), ()))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect((1, 2, 3), [1]), [1]))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect((1, 2, 3), [2]), [2]))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect((1, 2, 3), (1, 2, 3)), (1, 2, 3)))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect((1, (2, 4), 3), (1, 2, 3)), (1, 3)))
        self.assertTrue(Shared.ReallyEqual(Shared.Intersect((1, (2, 4), 3), (1, (2, 4), 3)), (1, (2, 4), 3)))

    def testException(self):
        self.assertTrue(Shared.ReallyEqual(Shared.Except((), ()), ()))
        self.assertTrue(Shared.ReallyEqual(Shared.Except((), (1, 2, 3)), ()))
        self.assertTrue(Shared.ReallyEqual(Shared.Except((1, 2, 3), [1]), (2, 3)))
        self.assertTrue(Shared.ReallyEqual(Shared.Except((1, 2, 3), [2]), (1, 3)))
        self.assertTrue(Shared.ReallyEqual(Shared.Except((1, 2, 3), (1, 2, 3)), ()))
        self.assertTrue(Shared.ReallyEqual(Shared.Except((1, (2, 4), 3), (1, 2, 3)), [(2, 4)]))
        self.assertTrue(Shared.ReallyEqual(Shared.Except((1, (2, 4), 3), [(2, 4)]), (1, 3)))

    def testUnion(self):
        self.assertTrue(Shared.ReallyEqual(Shared.Union((), ()), ()))
        self.assertTrue(Shared.ReallyEqual(Shared.Union((), (1, 2, 3)), (1, 2, 3)))
        self.assertTrue(Shared.ReallyEqual(Shared.Union((1, 2, 3), [1]), (1, 2, 3)))
        self.assertTrue(Shared.ReallyEqual(Shared.Union((1, 2, 3), (1, 2, 3)), (1, 2, 3)))
        self.assertTrue(Shared.ReallyEqual(Shared.Union((1, (2, 4), 3), (1, 2, 3)), [1, (2, 4), 3, 2]))
        self.assertTrue(Shared.ReallyEqual(Shared.Union((1, (2, 4), 3), [(2, 4)]), (1, (2, 4), 3)))

    def testNearby(self):
        pos = Shared.CellsNearby((0, 0))
        ans = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)]
        self.assertTrue((Shared.ReallyEqual(Shared.Intersect(ans, pos), ans)))

        pos = Shared.CellsNearby((1, 0))
        ans = [(0, 0), (2, 0), (1, -1), (1, 1), (0, -1), (0, 1)]
        self.assertTrue((Shared.ReallyEqual(Shared.Intersect(ans, pos), ans)))

        pos = Shared.CellsNearby((-1, 0))
        ans = [(-2, 0), (0, 0), (-1, -1), (-1, 1), (-2, -1), (-2, 1)]
        self.assertTrue((Shared.ReallyEqual(Shared.Intersect(ans, pos), ans)))

        pos = Shared.CellsNearby((0, 1))
        ans = [(-1, 1), (1, 1), (0, 0), (0, 2), (1, 0), (1, 2)]
        self.assertTrue((Shared.ReallyEqual(Shared.Intersect(ans, pos), ans)))

        pos = Shared.CellsNearby((0, -1))
        ans = [(-1, -1), (1, -1), (0, -2), (0, 0), (1, -2), (1, 0)]
        self.assertTrue((Shared.ReallyEqual(Shared.Intersect(ans, pos), ans)))

if __name__ == '__main__':
    unittest.main()