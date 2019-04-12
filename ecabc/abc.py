#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.2.2.3
#
#  Developed in 2019 by Sanskriti Sharma <sanskriti_sharma@student.uml.edu>
#  & Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This file implements an artificial bee colony to tune user-supplied
#  function parameters
#

# Stdlib imports
import os.path
from random import randint
import multiprocessing
from copy import deepcopy

# 3rd party imports
import numpy as np
from colorlogging import ColorLogger
try:
    import ujson as json
except:
    import json as json

# ECabc imports
from ecabc.bees import OnlookerBee, EmployerBee


class ABC:

    def __init__(self, fitness_fxn, num_employers=50, value_ranges=[],
                 print_level='info', file_logging='disable', args={},
                 processes=4):
        '''ABC object: manages employer and onlooker bees to optimize a set
        of generic values for a user-supplied fitness function. Handles data
        transfer and manipulation between bees.

        Args:
            fitness_fxn (callable): fitness function supplied by the user;
                should accept a tuple of tunable ints/floats, and optionally
                additional user-defined arguments (kwargs)
            num_employers (int): number of employer bees the colony utilizes
            value_ranges (list): each element defines a tunable variable in
                the form "(type ('int' or 'float'), (min_val, max_val))";
                initial, random values for each bee will between "min_val" and
                "max_val"
            print_level (string): console logging level: "debug", "info",
                "warn", "crit", "error", "disable"
            file_logging (string): file logging level: "debug", "info", "warn",
                "crit", "error", "disable"
            args (dict): additional user-defined arguments to pass to fitness
                function; these are not tuned
            processes (int): number of concurrent processes the algorithm will
                utililze via multiprocessing.Pool

        Return:
            None
        '''

        self._logger = ColorLogger(
            stream_level=print_level,
            file_level=file_logging
        )
        self._value_ranges = value_ranges
        if num_employers < 2:
            self._logger.log(
                'warn',
                'Two employers are needed: setting to two'
            )
            num_employers = 2
        self._num_employers = num_employers
        self._best_values = []
        self._best_score = None
        self._best_error = None
        self._minimize = True
        self._fitness_fxn = fitness_fxn
        self.__onlooker = OnlookerBee()
        self._limit = num_employers*len(value_ranges)
        self._employers = []
        self._args = args
        self._total_score = 0
        self._cycle_number = 0
        self._processes = processes

        if self._processes > 1:
            self._pool = multiprocessing.Pool(self._processes)
        else:
            self._pool = None

        if not callable(self._fitness_fxn):
            raise ValueError('submitted *fitness_fxn* is not callable')

    def add_argument(self, arg_name, arg_value):
        '''Add an additional argument to be passed to the fitness function
        via additional arguments dictionary; this argument/value is not tuned

        Args:
            arg_name (string): name/dictionary key of argument
            arg_value (any): dictionary value of argument
        '''

        if len(self._employers) > 0:
            self._logger.log(
                'warn',
                'Adding an argument after the employers have been created'
            )
        if self._args is None:
            self._args = {}
        self._args[arg_name] = arg_value

    def add_value(self, value_type, value_min, value_max):
        '''Add a tunable value to the ABC (fitness function must be
        configured to handle it)

        Args:
            value_type (string): type of the value, 'int' or 'float'
            value_min (int or float): minimum bound for the value
            value_max (int or float): maximum bound for the value

        Returns:
            None
        '''

        if len(self._employers) > 0:
            self._logger.log(
                'warn',
                'Adding a value after employers have been created'
            )
        value = (value_type,  (value_min, value_max))
        self._value_ranges.append(value)
        self._limit = self._num_employers*len(self._value_ranges)
        self._logger.log(
            'debug',
            'Limit set to {}'.format(self._limit)
        )

    @property
    def args(self):
        '''Arguments that will be passed to the fitness function at runtime'''

        return self._args

    @args.setter
    def args(self, args):
        '''Set additional arguments to be passed to the fitness function

        Args:
            args (dict): additional arguments
        '''
        self._args = args
        self._logger.log('debug', 'Args set to {}'.format(args))

    @property
    def minimize(self):
        '''If True, minimizes fitness function return value rather than
        derived score
        '''

        return self._minimize

    @minimize.setter
    def minimize(self, minimize):
        '''Configures the ABC to minimize fitness function return value or
        derived score

        Args:
            minimize (bool): if True, minimizes fitness function return value;
                if False, minimizes derived score
        '''

        self._minimize = minimize
        self._logger.log('debug', 'Minimize set to {}'.format(minimize))

    @property
    def num_employers(self):
        '''Number of employer bees present in the ABC'''

        return self._num_employers

    @num_employers.setter
    def num_employers(self, num_employers):
        '''Sets the number of employer bees; at least two are required

        Args:
            num_employers (int): number of employer bees
        '''

        if num_employers < 2:
            self._logger.log(
                'warn',
                'Two employers are needed: setting to two'
            )
            num_employers = 2
        self._num_employers = num_employers
        self._logger.log('debug', 'Number of employers set to {}'.format(
            num_employers
        ))
        self._limit = num_employers * len(self._value_ranges)
        self._logger.log('debug', 'Limit set to {}'.format(self._limit))

    @property
    def value_ranges(self):
        '''Value types, min/max values for tunable parameters'''

        return self._value_ranges

    @value_ranges.setter
    def value_ranges(self, value_ranges):
        '''Set the types, min/max values for tunable parameters

        Args:
            value_ranges (list): each element defines a tunable variable in
                the form "(type ('int' or 'float'), (min_val, max_val))";
                initial, random values for each bee will between "min_val" and
                "max_val"
        '''

        self._value_ranges = value_ranges
        self._logger.log('debug', 'Value ranges set to {}'.format(
            value_ranges
        ))

    @property
    def best_performer(self):
        '''Return the best performing values: (score, values, error)'''

        return (self._best_score, self._best_values, self._best_error)

    @property
    def best_employers(self):
        '''Return a list of best performing employer bees'''

        return self.__onlooker.best_employers

    @property
    def limit(self):
        '''Maximum number of cycles a bee is allowed to stay at its current
        food source before abandoning it (moving to a randomly generated one)
        '''

        return self._limit

    @limit.setter
    def limit(self, limit):
        '''Set the maximum number of cycles a bee is allowed to stay at its
        current food source before abandoning it (moving to a randomly
        generated one); by default, this is set to the number of employers
        times the number of tunable values

        Args:
            limit (int): maximum number of cycles
        '''

        self._limit = limit

    @property
    def processes(self):
        '''How many concurrent processes the ABC will utililze for fitness
        function evaluation via multiprocessing.Pool
        '''

        return self._processes

    @processes.setter
    def processes(self, processes):
        '''Set the number of concurrent processes the ABC will utilize for
        fitness function evaluation; if <= 1, single process is used

        Args:
            processes (int): number of concurrent processes
        '''

        if self._processes > 1:
            self._pool.close()
            self._pool.join()
            self._pool = multiprocessing.Pool(processes)
        else:
            self._pool = None
        self._logger.log('debug', 'Number of processes set to {}'.format(
            processes
        ))

    def infer_process_count(self):
        '''Infers the number of CPU cores in the current system, sets the
        number of concurrent processes accordingly
        '''

        try:
            self.processes = multiprocessing.cpu_count()
        except NotImplementedError:
            self._logger.log(
                'error',
                'Could infer CPU count, setting number of processes back to 4'
            )
            self.processes = 4

    def create_employers(self):
        '''Generate employer bees. This should be called directly after the
        ABC is initialized.
        '''

        self.__verify_ready(True)
        employers = []
        for i in range(self._num_employers):
            employer = EmployerBee(self.__gen_random_values())
            if self._processes <= 1:
                employer.error = self._fitness_fxn(
                    employer.values, **self._args
                )
                employer.score = employer.get_score()
                if np.isnan(employer.score):
                    self._logger.log('warn', 'NaN bee score: {}, {}'.format(
                        employer.id, employer.score
                    ))
                self._logger.log('debug', 'Bee number {} created'.format(
                    i + 1
                ))
                self.__update(employer.score, employer.values, employer.error)
            else:
                employer.error = self._pool.apply_async(
                    self._fitness_fxn,
                    [employer.values],
                    self._args
                )
                employers.append(employer)
            self._employers.append(employer)
        for idx, employer in enumerate(employers):
            try:
                employer.error = employer.error.get()
                employer.score = employer.get_score()
                if np.isnan(employer.score):
                    self._logger.log('warn', 'NaN bee score: {}, {}'.format(
                        employer.id, employer.score
                    ))
                self._logger.log('debug', 'Bee number {} created'.format(
                    i + 1
                ))
                self.__update(employer.score, employer.values, employer.error)
            except Exception as e:
                raise e
        self._logger.log('debug', 'Employer creation complete')

    def run_iteration(self):
        '''Runs a single iteration of the ABC; employer phase -> probability
        calculation -> onlooker phase -> check positions
        '''

        self._employer_phase()
        self._calc_probability()
        self._onlooker_phase()
        self._check_positions()

    def _employer_phase(self):
        '''Iterates through the employer bees and merges each with another
        random bee (one value is moved in accordance with the second bee's
        value); if the mutation performs better, the bee is moved to the new
        position
        '''

        self._logger.log('debug', 'Employer bee phase')
        modified = []
        for bee in self._employers:
            if self._processes <= 1:
                new_values = self._merge_bee(bee)
                self._move_bee(bee, new_values)
            else:
                modified.append((
                    bee,
                    self._pool.apply_async(self._merge_bee, [bee])
                ))
        for pair in modified:
            self._move_bee(pair[0], pair[1].get())

    def _calc_probability(self):
        '''Determines the probability that each bee will be chosen during the
        onlooker phase; also determines if a new best-performing bee is found
        '''

        self._logger.log('debug', 'Calculating bee probabilities')
        self.__verify_ready()
        self._total_score = 0
        for employer in self._employers:
            self._total_score += employer.score
            if self.__update(employer.score, employer.values, employer.error):
                self._logger.log(
                    'info',
                    'Update to best performer -'
                    ' error: {} | score: {} | values: {}'.format(
                        employer.error,
                        employer.score,
                        employer.values
                    )
                )
        for employer in self._employers:
            employer.calculate_probability(self._total_score)

    def _onlooker_phase(self):
        '''Well-performing bees (chosen probabilistically based on fitness
        score) have a value merged with a second random bee
        '''

        self.__verify_ready()
        self._logger.log('debug', 'Onlooker bee phase')
        modified = []
        for _ in self._employers:
            chosen_bee = np.random.choice(
                self._employers,
                p=[e.probability for e in self._employers]
            )
            if self._processes <= 1:
                new_values = self._merge_bee(chosen_bee)
                self._move_bee(chosen_bee, new_values)
                self.__update(
                    chosen_bee.score,
                    chosen_bee.values,
                    chosen_bee.error
                )
            else:
                modified.append((
                    chosen_bee,
                    self._pool.apply_async(self._merge_bee, [chosen_bee])
                ))
        for pair in modified:
            self._move_bee(pair[0], pair[1].get())
            self.__update(pair[0].score, pair[0].values, pair[0].error)

    def _check_positions(self):
        '''Checks each bee to see if it abandons its current food source (has
        not found a better one in self._limit iterations); if abandoning, it
        becomes a scout and generates a new, random food source
        '''

        self.__verify_ready()
        max_trials = 0
        scout = None
        for bee in self._employers:
            if (bee.failed_trials >= max_trials):
                max_trials = bee.failed_trials
                scout = bee
        if scout is not None and scout.failed_trials > self._limit:
            self._logger.log(
                'debug',
                'Sending scout (error of {} with limit of {})'.format(
                    scout.error, scout.failed_trials
                )
            )
            scout.values = self.__gen_random_values()

    def _merge_bee(self, bee):
        '''Shifts a random value for a supplied bee with in accordance with
        another random bee's value

        Args:
            bee (EmployerBee): supplied bee to merge

        Returns:
            tuple: (score of new position, values of new position, fitness
                function return value of new position)
        '''

        random_dimension = randint(0, len(self._value_ranges) - 1)
        second_bee = randint(0, self._num_employers - 1)
        while (bee.id == self._employers[second_bee].id):
            second_bee = randint(0, self._num_employers - 1)
        new_bee = deepcopy(bee)
        new_bee.values[random_dimension] = self.__onlooker.calculate_positions(
            new_bee.values[random_dimension],
            self._employers[second_bee].values[random_dimension],
            self._value_ranges[random_dimension]
        )
        fitness_score = new_bee.get_score(self._fitness_fxn(
            new_bee.values,
            **self._args
        ))
        return (fitness_score, new_bee.values, new_bee.error)

    def _move_bee(self, bee, new_values):
        '''Moves a bee to a new position if new fitness score is better than
        the bee's current fitness score

        Args:
            bee (EmployerBee): bee to move
            new_values (tuple): (new score, new values, new fitness function
                return value)
        '''

        score = np.nan_to_num(new_values[0])
        if bee.score > score:
            bee.failed_trials += 1
        else:
            bee.values = new_values[1]
            bee.score = score
            bee.error = new_values[2]
            bee.failed_trials = 0
            self._logger.log('debug', 'Bee assigned to new merged position')

    def __update(self, score, values, error):
        '''Update the best score and values if the given score is better than
        the current best score

        Args:
            score (float): new score to evaluate
            values (list): new value ranges to evaluate
            error (float): new fitness function return value to evaluate

        Returns:
            bool: True if new score is better, False otherwise
        '''

        if self._minimize:
            if self._best_score is None or score > self._best_score:
                self._best_score = score
                self._best_values = values.copy()
                self._best_error = error
                self._logger.log(
                    'debug',
                    'New best food source memorized: {}'.format(
                        self._best_error
                    )
                )
                return True
        elif not self._minimize:
            if self._best_score is None or score < self._best_score:
                self._best_score = score
                self._best_values = values.copy()
                self._best_error = error
                self._logger.log(
                    'debug',
                    'New best food source memorized: {}'.format(
                        self._best_error
                    )
                )
                return True
        return False

    def __gen_random_values(self):
        '''Generate random values based on supplied value ranges

        Returns:
            list: random values, one per tunable variable
        '''

        values = []
        if self._value_ranges is None:
            self._logger.log(
                'crit',
                'Must set the type/range of possible values'
            )
            raise RuntimeError("Must set the type/range of possible values")
        else:
            for t in self._value_ranges:
                if t[0] == 'int':
                    values.append(randint(t[1][0], t[1][1]))
                elif t[0] == 'float':
                    values.append(np.random.uniform(t[1][0], t[1][1]))
                else:
                    self._logger.log(
                        'crit',
                        'Value type must be either an `int` or a `float`'
                    )
                    raise RuntimeError(
                        'Value type must be either an `int` or a `float`'
                    )
        return values

    def __verify_ready(self, creating=False):
        '''Some cleanup, ensures that everything is set up properly to avoid
        random errors during execution

        Args:
            creating (bool): True if currently creating employer bees, False
                for checking all other operations
        '''

        if len(self._value_ranges) == 0:
            self._logger.log(
                'crit',
                'Attribute value_ranges must have at least one value'
            )
            raise RuntimeWarning(
                'Attribute value_ranges must have at least one value'
            )
        if len(self._employers) == 0 and creating is False:
            self._logger.log('crit', 'Need to create employers')
            raise RuntimeWarning('Need to create employers')

    def import_settings(self, filename):
        '''Import settings from a JSON file

        Args:
            filename (string): name of the file to import from
        '''

        if not os.path.isfile(filename):
            self._logger.log(
                'error',
                'File: {} not found, continuing with default settings'.format(
                    filename
                )
            )
        else:
            with open(filename, 'r') as jsonFile:
                data = json.load(jsonFile)
                self._value_ranges = data['valueRanges']
                self._best_values = data['best_values']
                self._best_values = []
                for index, value in enumerate(data['best_values']):
                    if self._value_ranges[index] == 'int':
                        self._best_values.append(int(value))
                    else:
                        self._best_values.append(float(value))
                self.minimize = data['minimize']
                self.num_employers = data['num_employers']
                self._best_score = float(data['best_score'])
                self.limit = data['limit']

    def save_settings(self, filename):
        '''Save settings to a JSON file

        Arge:
            filename (string): name of the file to save to
        '''

        data = dict()
        data['valueRanges'] = self._value_ranges
        data['best_values'] = [str(value) for value in self._best_values]
        data['minimize'] = self._minimize
        data['num_employers'] = self._num_employers
        data['best_score'] = str(self._best_score)
        data['limit'] = self._limit
        data['best_error'] = self._best_error
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

    def __getstate__(self):
        '''Returns appropriate dictionary for correctly pickling the ABC
        object in case of multiprocssing
        '''

        state = self.__dict__.copy()
        del state['_logger']
        del state['_pool']
        return state
