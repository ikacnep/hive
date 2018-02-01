import unittest

from ...Game.Utils.NegArray import NegArray


class NegArrayTests(unittest.TestCase):
    def testAll(self):
        narr = NegArray(3)
        self.assertEqual(3, narr.Dim())
        for i in range(0, 3):
            self.assertEqual(narr.Count(i), 0)
            self.assertIsNone(narr.Get((i, i, i)))

        with self.assertRaises(IndexError):
            narr.Put(0, (1, 2))

        with self.assertRaises(IndexError):
            narr.Put(0, (1, 2, 3, 4))

        narr.Put(6, (1, 2, 3))
        narr.Put(4, (-1, 2, 3))
        narr.Put(2, (1, -2, 3))
        narr.Put(0, (-1, -2, 3))
        narr.Put(0, (1, 2, -3))
        narr.Put(-2, (-1, 2, -3))
        narr.Put(-4, (1, -2, -3))
        narr.Put(-6, (-1, -2, -3))

        for i in range(-3, 3):
            for j in range(-3, 3):
                for k in range(-3, 3):
                    try:
                        val = narr.Get((i, j, k))
                    except:
                        self.fail("Exception at: " + repr(i) + ", " + repr(j) + ", " + repr(k))

                    if abs(i) == 1 and abs(j) == 2 and abs(k) == 3:
                        self.assertEqual(
                            i + j + k,
                            val,
                            msg="Wrong value: " + repr(val) + " at: " + repr(i) + ", " + repr(j) + ", " + repr(k)
                        )
                    else:
                        self.assertIsNone(val, msg="Not none found at: " + repr(i) + ", " + repr(j) + ", " + repr(k))


if __name__ == '__main__':
    unittest.main()
