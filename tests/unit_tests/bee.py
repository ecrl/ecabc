import unittest

from ecabc import Bee


class TestBee(unittest.TestCase):

    def test_bee_init(self):

        bee = Bee([0, 0, 0], 0, 1, True)
        self.assertTrue(bee._is_employer)

        bee = Bee([0, 0, 0], 0, 1)
        self.assertFalse(bee._is_employer)

        bee = Bee([0, 0, 0], 0, 1)
        self.assertEqual(bee._params, [0, 0, 0])
        self.assertEqual(bee._obj_fn_val, 0)
        self.assertEqual(bee._fitness_score, 1)
        self.assertEqual(bee._stay_limit, 1)

    def test_abandon(self):

        bee = Bee([0, 0, 0], 0, 2)
        result = bee.abandon
        self.assertFalse(result)
        result = bee.abandon
        self.assertTrue(result)

    def test_calc_fitness(self):

        result = Bee.calc_fitness(0)
        self.assertEqual(result, 1)
        result = Bee.calc_fitness(-1)
        self.assertEqual(result, 2)

    def test_is_better_food(self):

        bee = Bee([0, 0, 1], 1, 1)
        result = bee.is_better_food(0)
        self.assertTrue(result)
        result = bee.is_better_food(2)
        self.assertFalse(result)


if __name__ == '__main__':

    unittest.main()
