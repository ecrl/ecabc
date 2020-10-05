import unittest

from ecabc import ABC


def objective_function(params):
    return sum(params)


def objective_function_kwargs(params, my_kwarg):
    return sum(params) + my_kwarg


class TestColony(unittest.TestCase):

    def test_colony_init(self):

        c = ABC(10, objective_function)
        self.assertEqual(c._num_employers, 10)
        self.assertEqual(c._obj_fn, objective_function)

        kwargs = {'my_kwarg', 2}
        c = ABC(10, objective_function, kwargs)
        self.assertEqual(c._obj_fn_args, kwargs)

        c = ABC(10, objective_function, num_processes=8)
        self.assertEqual(c._num_processes, 8)

        try:
            c = ABC(10, None)
        except Exception as E:
            self.assertEqual(type(E), ReferenceError)

    def test_no_bees(self):

        c = ABC(10, objective_function)
        self.assertEqual(c.best_fitness, 0)
        self.assertEqual(c.best_ret_val, None)
        self.assertEqual(c.best_params, {})
        self.assertEqual(c.average_fitness, None)
        self.assertEqual(c.average_ret_val, None)

        try:
            c.search()
        except Exception as E:
            self.assertEqual(type(E), RuntimeError)

    def test_add_parameter(self):

        c = ABC(10, objective_function)
        c.add_param(0, 1)
        c.add_param(2, 3)
        c.add_param(4, 5)
        self.assertEqual(len(c._params), 3)
        self.assertEqual(c._params[0]._min_val, 0)
        self.assertEqual(c._params[0]._max_val, 1)
        self.assertEqual(c._params[1]._min_val, 2)
        self.assertEqual(c._params[1]._max_val, 3)
        self.assertEqual(c._params[2]._min_val, 4)
        self.assertEqual(c._params[2]._max_val, 5)
        self.assertEqual(c._params[0]._dtype, int)
        c.add_param(0.0, 1.0)
        self.assertEqual(c._params[3]._dtype, float)
        self.assertTrue(c._params[0]._restrict)
        c.add_param(0, 1, False)
        self.assertFalse(c._params[4]._restrict)

    def test_initialize(self):

        c = ABC(10, objective_function)
        c.add_param(0, 10)
        c.add_param(0, 10)
        c.initialize()
        self.assertEqual(len(c._bees), 20)

    def test_get_stats(self):

        c = ABC(10, objective_function)
        c.add_param(0, 0)
        c.add_param(0, 0)
        c.initialize()
        self.assertEqual(c.best_fitness, 1)
        self.assertEqual(c.best_ret_val, 0)
        self.assertEqual(c.best_params, {'P0': 0, 'P1': 0})
        self.assertEqual(c.average_fitness, 1)
        self.assertEqual(c.average_ret_val, 0)

    def test_kwargs(self):

        c = ABC(10, objective_function_kwargs, {'my_kwarg': 2})
        c.add_param(0, 0)
        c.add_param(0, 0)
        c.initialize()
        self.assertEqual(c.best_ret_val, 2)

    def test_search(self):

        c = ABC(20, objective_function)
        c.add_param(0, 10)
        c.add_param(0, 10)
        c.initialize()
        for _ in range(50):
            c.search()
        self.assertEqual(c.best_fitness, 1)
        self.assertEqual(c.best_ret_val, 0)
        self.assertEqual(c.best_params, {'P0': 0, 'P1': 0})

    def test_multiprocessing(self):

        c = ABC(20, objective_function, num_processes=4)
        self.assertEqual(c._num_processes, 4)
        c.add_param(0, 10)
        c.add_param(0, 10)
        c.initialize()
        c.search()

    def test_custom_param_name(self):

        c = ABC(20, objective_function)
        c.add_param(0, 10, name='int1')
        c.add_param(0, 10, name='int2')
        c.initialize()
        for _ in range(50):
            c.search()
        self.assertEqual(c.best_params, {'int1': 0, 'int2': 0})


if __name__ == '__main__':

    unittest.main()
