#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.3.0.0
#
#  Developed in 2019 by Sanskriti Sharma <sanskriti_sharma@student.uml.edu>,
#  Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>, and Travis Kessler
#  <Travis_Kessler@student.uml.edu>
#
#  abc.py: contains ABC object, handling the initialization and runtime of the
#  artificial bee colony
#

# Stdlib. imports
from multiprocessing import Pool
from random import randint
from typing import Callable, Any, Union
from warnings import warn

# ECabc imports
from ecabc.bee import Bee
from ecabc.parameter import Parameter
from ecabc.utils import apply_mutation, call_obj_fn, choose_bee,\
    determine_best_bee


class ABC:

    def __init__(self, num_employers: int,
                 objective_fn: Callable[[list], float], obj_fn_args: dict = {},
                 num_processes: int = 1):
        ''' ABC object: optimizes parameters for user-supplied function

        Args:
            num_employers (int): number of employer bees in the colony
            objective_fn (callable): function to optimize; accepts list of
                ints/floats, returns float (fitness)
            obj_fn_args (dict): non-tunable kwargs to pass to objective_fn
            num_processes (int): number of concurrent processes to utilize
        '''

        if not callable(objective_fn):
            raise ReferenceError('Supplied objective function not callable')
        self._obj_fn = objective_fn
        self._obj_fn_args = obj_fn_args
        self._num_employers = num_employers
        self._num_processes = num_processes
        self._params = []
        self._bees = []

    @property
    def best_fitness(self) -> float:
        ''' Returns fitness score from best-performing bee '''

        return determine_best_bee(self._bees)[0]

    @property
    def best_ret_val(self) -> Union[int, float]:
        ''' Returns objective_fn return value from best-performing bee '''

        return determine_best_bee(self._bees)[1]

    @property
    def best_params(self) -> list:
        ''' Returns parameters from best-performing bee '''

        return determine_best_bee(self._bees)[2]

    @property
    def average_fitness(self) -> float:
        ''' Returns average fitness score for bee population '''

        if len(self._bees) == 0:
            return None
        return (sum(b._fitness_score for b in self._bees) / len(self._bees))

    @property
    def average_ret_val(self) -> Union[int, float]:
        ''' Returns average objective_fn return value for bee population '''

        if len(self._bees) == 0:
            return None
        return (sum(b._obj_fn_val for b in self._bees) / len(self._bees))

    def add_param(self, min_val: Union[int, float], max_val: Union[int, float],
                  restrict: bool = True):
        ''' ABC.add_param: adds a parameter to be processed by the user-
        supplied objective function

        Args:
            min_val (int, float): minimum value allowed for the parameter's
                initialization
            max_val (int, float): maximum value allowed for the parameter's
                initialization
            restrict (bool): if `True`, parameter mutations must be within
                [min_val, max_val], `False` allows out-of-bounds mutation
        '''

        if len(self._bees) > 0:
            raise RuntimeError(
                'Cannot add another parameter after bee initialization'
            )
        self._params.append(Parameter(min_val, max_val, restrict))

    def initialize(self):
        ''' ABC.initialize: creates `num_employers` employer bees and
        `num_employers` onlooker bees
        '''

        if len(self._bees) > 0:
            warn('initialize() called again: overwriting bee population',
                 RuntimeWarning)

        self._bees = []

        if self._num_processes > 1:
            employer_pool = Pool(processes=self._num_processes)
        employer_results = []

        for _ in range(self._num_employers):

            params = [p.rand_val for p in self._params]
            if self._num_processes > 1:
                employer_results.append(employer_pool.apply_async(
                    call_obj_fn, [params, self._obj_fn, self._obj_fn_args]
                ))
            else:
                employer_results.append(call_obj_fn(
                    params, self._obj_fn, self._obj_fn_args
                ))

        if self._num_processes > 1:

            employer_pool.close()
            employer_pool.join()
            employer_results = [r.get() for r in employer_results]

        for result in employer_results:

            self._bees.append(Bee(
                result[0],
                result[1],
                len(self._params) * self._num_employers,
                True
            ))

        if self._num_processes > 1:
            onlooker_pool = Pool(processes=self._num_processes)
        onlooker_results = []

        for _ in range(self._num_employers):

            chosen_employer = choose_bee(self._bees)
            neighbor_food = apply_mutation(
                chosen_employer._params, self._params
            )

            if self._num_processes > 1:
                onlooker_results.append(onlooker_pool.apply_async(
                    call_obj_fn,
                    [neighbor_food, self._obj_fn, self._obj_fn_args]
                ))
            else:
                onlooker_results.append(call_obj_fn(
                    neighbor_food, self._obj_fn, self._obj_fn_args
                ))

        if self._num_processes > 1:

            onlooker_pool.close()
            onlooker_pool.join()
            onlooker_results = [r.get() for r in onlooker_results]

        for result in onlooker_results:

            self._bees.append(Bee(
                result[0],
                result[1],
                len(self._params) * self._num_employers,
            ))

    def search(self):
        ''' ABC.search: performs one "search cycle" for all bees in the
        colony; a search cycle consists of:

        for all bees:
            if bee has exhausted its current food source:
                if bee is an employer, find a new random food source
                if bee is an onlooker, travel to a food source near a well-
                    performing bee's food source
            if bee has not exhausted its current food source:
                mutate one parameter value, move to food source if better;
                    else, stay at current food source
        bees = updated bee states

        Exhaustion is defined as the maximum number of search cycles a bee is
        allowed to stay at its current food source, given by EX = NE * D, where
        NE is the number of employers and D is the dimensionality of the
        problem (number of parameters)
        '''

        if len(self._bees) == 0:
            raise RuntimeError('search() cannot be called before initialize()')

        if self._num_processes > 1:
            bee_pool = Pool(processes=self._num_processes)
        new_employer_results = []
        new_onlooker_results = []
        new_position_results = []
        current_positions = []

        for bee in self._bees:

            if bee.abandon:

                if bee._is_employer:

                    new_params = [p.rand_val for p in self._params]
                    if self._num_processes > 1:
                        new_employer_results.append(bee_pool.apply_async(
                            call_obj_fn,
                            [new_params, self._obj_fn, self._obj_fn_args]
                        ))
                    else:
                        new_employer_results.append(call_obj_fn(
                            new_params, self._obj_fn, self._obj_fn_args
                        ))

                else:

                    chosen_bee = choose_bee(self._bees)
                    neighbor_food = apply_mutation(
                        chosen_bee._params, self._params
                    )
                    if self._num_processes > 1:
                        new_onlooker_results.append(bee_pool.apply_async(
                            call_obj_fn,
                            [neighbor_food, self._obj_fn, self._obj_fn_args]
                        ))
                    else:
                        new_onlooker_results.append(call_obj_fn(
                            neighbor_food, self._obj_fn, self._obj_fn_args
                        ))

            else:

                current_positions.append(bee)
                neighbor_food = apply_mutation(bee._params, self._params)
                if self._num_processes > 1:
                    new_position_results.append(bee_pool.apply_async(
                        call_obj_fn,
                        [neighbor_food, self._obj_fn, self._obj_fn_args]
                    ))
                else:
                    new_position_results.append(call_obj_fn(
                        neighbor_food, self._obj_fn, self._obj_fn_args
                    ))

        if self._num_processes > 1:

            bee_pool.close()
            bee_pool.join()
            new_employer_results = [r.get() for r in new_employer_results]
            new_onlooker_results = [r.get() for r in new_onlooker_results]
            new_position_results = [r.get() for r in new_position_results]

        next_bee_generation = []

        for result in new_employer_results:

            next_bee_generation.append(Bee(
                result[0],
                result[1],
                len(self._params) * self._num_employers,
                True
            ))

        for result in new_onlooker_results:

            next_bee_generation.append(Bee(
                result[0],
                result[1],
                len(self._params) * self._num_employers
            ))

        for idx, result in enumerate(new_position_results):

            bee_to_compare = current_positions[idx]
            if bee_to_compare.is_better_food(result[1]):
                if bee._is_employer:
                    next_bee_generation.append(Bee(
                        result[0],
                        result[1],
                        len(self._params) * self._num_employers,
                        True
                    ))
                else:
                    next_bee_generation.append(Bee(
                        result[0],
                        result[1],
                        len(self._params) * self._num_employers
                    ))
            else:
                next_bee_generation.append(bee_to_compare)

        self._bees = next_bee_generation
