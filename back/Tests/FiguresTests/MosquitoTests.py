import unittest
from Game.Utils.NegArray import NegArray
from Game.Settings.Figures.FigureTypes import FigureType
import Shared

class MosquitoTests(unittest.TestCase):
    def testAll(self):
        field = NegArray(2)
        mosquito = self.putMosquito((0, 0), field)
        turns = mosquito.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        mosquito.ResetAvailTurns()

        self.putMosquito((1, 0), field)
        turns = mosquito.AvailableTurns(field)
        self.assertEqual(len(turns), 0)
        mosquito.ResetAvailTurns()

        # Fuck this... =/


    def putMosquito(self, pos, field):
        q = FigureType.Mosquito.GetFigure(0, pos)
        field.Put([q], pos)
        return q

if __name__ == '__main__':
    unittest.main()