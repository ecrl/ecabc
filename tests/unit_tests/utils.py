import unittest

import ecabc.utils as abc_utils
from ecabc import Bee, Parameter


class TestUtils(unittest.TestCase):

    def test_apply_mutation(self):

        params = [Parameter(0, 10, True) for _ in range(3)]
        curr_params = [5, 5, 5]
        mut_params = abc_utils.apply_mutation(curr_params, params)
        self.assertNotEqual(curr_params, mut_params)

    def test_call_obj_fn(self):

        def obj_fn(params):
            return sum(params)

        def obj_fn_kw(params, my_kwarg):
            return sum(params) + my_kwarg

        param_vals = [2, 2, 2]

        ret_params, result = abc_utils.call_obj_fn(param_vals, obj_fn, {})
        self.assertEqual(6, result)
        self.assertEqual(param_vals, ret_params)

        fn_args = {'my_kwarg': 2}
        ret_params, result = abc_utils.call_obj_fn(
            param_vals, obj_fn_kw, fn_args
        )
        self.assertEqual(8, result)
        self.assertEqual(param_vals, ret_params)

    def test_choose_bee(self):

        bee_1 = Bee([0], 100000000000000000000, 0)
        bee_2 = Bee([0], 0, 0)
        chosen_bee = abc_utils.choose_bee([bee_1, bee_2])
        self.assertEqual(chosen_bee, bee_2)

    def test_determine_best_bee(self):

        bee_1 = Bee([10], 10, 0)
        bee_2 = Bee([0], 0, 0)
        bee_2_fitness = bee_2._fitness_score
        bee_2_ret_val = bee_2._obj_fn_val
        bee_2_params = bee_2._params
        _fit, _ret, _param = abc_utils.determine_best_bee([bee_1, bee_2])
        self.assertEqual(_fit, bee_2_fitness)
        self.assertEqual(_ret, bee_2_ret_val)
        self.assertEqual(_param, bee_2_params)


if __name__ == '__main__':

    unittest.main()
