import unittest

from ecabc import Parameter


class TestParameter(unittest.TestCase):

    def test_param_init(self):

        param = Parameter(0, 10, False)
        self.assertFalse(param._restrict)

        param = Parameter(0, 10)
        self.assertTrue(param._restrict)

        param = Parameter(0, 10)
        self.assertEqual(param._dtype, int)
        self.assertEqual(param._min_val, 0)
        self.assertEqual(param._max_val, 10)

        param = Parameter(0.0, 10.0)
        self.assertEqual(param._dtype, float)
        self.assertEqual(param._min_val, 0.0)
        self.assertEqual(param._max_val, 10.0)

    def test_rand_val(self):

        param = Parameter(0, 10)
        rand_val = param.rand_val
        self.assertGreaterEqual(rand_val, 0)
        self.assertLessEqual(rand_val, 10)
        self.assertEqual(type(rand_val), int)

        param = Parameter(0.0, 10.0)
        rand_val = param.rand_val
        self.assertEqual(type(rand_val), float)

    def test_mutate(self):

        param = Parameter(0, 10)
        rand_val = param.rand_val
        for _ in range(1000):
            mutation = param.mutate(rand_val)
            if mutation < 0 or mutation > 10:
                raise ValueError('Mutation outside min/max bounds')

        param = Parameter(0, 3, False)
        rand_val = param.rand_val
        outside_bounds = False
        mutation = param.mutate(rand_val)
        while True:
            if mutation < 0 or mutation > 3:
                outside_bounds = True
                break
            mutation = param.mutate(mutation)
        self.assertTrue(
            outside_bounds, 'Mutation did not occur outside min/max bounds'
        )


if __name__ == '__main__':

    unittest.main()
