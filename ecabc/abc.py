#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.2.2.0
#  Developed in 2018 by Sanskriti Sharma <sanskriti_sharma@student.uml.edu> & Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program implements an artificial bee colony to tune ecnet hyperparameters
#

import sys as sy
import os.path
from random import randint
import numpy as np
from colorlogging import ColorLogger
import pickle
import multiprocessing
from copy import deepcopy

try:
    import ujson as json
except:
    import json as json

# artificial bee colony packages
from ecabc.bees import OnlookerBee, EmployerBee


class ABC:

    '''
    ABC object: Manages employer and onlooker bees to optimize a set of generic values
    given a generic user defined fitness function. Handles data transfer and manipulation
    between bees.
    '''

    def __init__(self, fitness_fxn, num_employers=50, value_ranges=[],num_dimension=6, print_level='info', file_logging='disable', args={}, processes=4):
        self._logger = ColorLogger(stream_level=print_level, file_level=file_logging)
        self._value_ranges = value_ranges
        self._num_employers = num_employers
        self._best_values = []
        self._best_score = None
        self._best_error = None
        self._minimize = False #minimizes score not error
        self._fitness_fxn = fitness_fxn
        self.__onlooker = OnlookerBee()
        self._limit = num_employers*num_dimension
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
        '''
        Add an argument that will be processed by the fitness
        function. Doing this after you have initiliazed the abc
        employers and have started running the abc may produce
        some weird results\n

        Args:\n
        arg_name: The keyword name of your argument\n
        arg_value: The value of the given argument
        '''
        if len(self._employers) > 0:
            self._logger.log('warn', 'Adding an argument after the employers have been created')
        if self._args is None:
            self._args = {}
        self._args[arg_name] = arg_value

    def add_value(self, value_type, value_min, value_max):
        '''
        Add another value that will be factored into the calculation
        of the bee's fitness. Calling this after the abc has run for
        a few iterations may produce wonky results\n
        Args:\n
        value_type: Either of type 'int' or type 'float'\n
        value_min: Minimum numerical value\n
        value_max: Maximum numerical value\n
        '''
        if len(self._employers) > 0:
            self._logger.log('warn', 'Adding a value after employers have been created')
        value = (value_type,  (value_min, value_max))
        self._value_ranges.append(value)

    @property
    def args(self):
        '''
        Arguments that will be passed to the fitness function at runtime
        '''
        return self._args

    @args.setter
    def args(self, args):
        self._args = args
        self._logger.log('debug', "Args set to {}".format(args))

    @property
    def minimize(self):
        '''
        Boolean value that describes whether the bee colony is minimizing
        or maximizing the generic fitness function
        '''
        return self._minimize

    @minimize.setter
    def minimize(self, minimize):
        self._minimize = minimize
        self._logger.log('debug', "Minimize set to {}".format(minimize))

    @property
    def num_employers(self):
        return self._num_employers

    @num_employers.setter
    def num_employers(self, num_employers):
        if num_employers < 10:
            self._logger.log('warn', "Cannot set num_employers to < 10, setting to 10")
            self._num_employers = 10
        else:
            self._num_employers = num_employers
            self._logger.log('debug', "Number of employers set to {}".format(num_employers))
        self._limit = num_employers * len(self._value_ranges)
        self._logger.log('info','Limit . is {} ({} * {})'.format(self._limit, num_employers, len(self._value_ranges)))

    @property
    def value_ranges(self):
        return self._value_ranges

    @value_ranges.setter
    def value_ranges(self, value_ranges):
        self._value_ranges = value_ranges
        self._logger.log('debug', "Value ranges set to {}".format(value_ranges))

    @property
    def best_performer(self):
        '''
        Return the best performing values: (score, values, error)
        '''
        return (self._best_score, self._best_values, self._best_error)

    @property
    def best_employers(self):
        '''
        Return a list of best performing employer bees
        '''
        return self.__onlooker.best_employers

    @property
    def limit(self):
        '''
        Get the maximum amount of times a bee can perform below average
        before completely abandoning its current food source and seeking
        a randomly generated one
        '''
        return self._limit

    @limit.setter
    def limit(self, limit):
        '''
        Set the maximum amount of times a bee can perform below average
        before completely bandoning its current food source and seeking
        a randomly generate done
        '''
        self._limit = limit

    @property
    def processes(self):
        '''
        Value which indicates how many processes are allowed to be a spawned
        for various methods/calculations at a time. If the number is less than 1,
        multiprocessing will be disabled and the program will run everything synchroniously
        '''
        return self._processes

    @processes.setter
    def processes(self, processes):
        if self._processes > 1:
            self._pool.close()
            self._pool.join()

        self._processes = processes
        if self._processes > 1:
            self._pool = multiprocessing.Pool(processes)
        else:
            self._pool = None
        self._logger.log('debug', "Number of processes set to {}".format(processes))

    def infer_process_count(self):
        '''
        Set the amount of processes that will be used to
        the amount of CPU's in your system 
        '''
        try:
            self.processes = multiprocessing.cpu_count()
        except NotImplementedError:
            self._logger.log('error', "Could not get cpu count, setting amount of processes back to 4")
            self.processes = 4

    def run_iteration(self):
        '''
        Run a single iteration of the bee colony. This will produce fitness scores
        for each bee, merge bees based on probabilities, and calculate new positions for
        bees if necessary. At the end of this method, the best_perforder attribute may
        or may not have been updated if a better food source was found
        '''
        self._employer_phase()
        self._calc_probability()
        self._onlooker_phase()
        self._check_positions()

    def create_employers(self):
        '''
        Generate a set of employer bees. This method must be called in order to generate a set
        of usable employers bees. Other methods depend on this.
        '''
        self.__verify_ready(True)
        employers = []
        for i in range(self._num_employers):
            employer = EmployerBee(self.__gen_random_values())
            if self._processes <= 1:
                employer.error = self._fitness_fxn(employer.values, **self._args)
                employer.score = employer.get_score()
                self._logger.log('debug', "Bee number {} created".format(i + 1))
                self.__update(employer.score, employer.values, employer.error)
            else:
                employer.error = self._pool.apply_async(self._fitness_fxn, [employer.values], self._args)
                employers.append(employer)
            self._employers.append(employer)
        for idx, employer in enumerate(employers):
            try:
                employer.error = employer.error.get()
                employer.score = employer.get_score()
                self._logger.log('debug', "Bee number {} created".format(idx + 1))
                self.__update(employer.score, employer.values, employer.error)
            except Exception as e:
                raise e
        self._logger.log('debug','Employer creation complete')

    def _employer_phase(self):
        self._logger.log('debug',"Employer bee phase")
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

    def _move_bee(self, bee, new_values):
        if bee.score > new_values[0]:
            bee.failed_trials += 1
        else:
            bee.values = new_values[1]
            bee.score = new_values[0]
            bee.error = new_values[2]
            bee.failed_trials = 0
            self._logger.log('debug', "Bee assigned to new merged position")

    def _onlooker_phase(self):
        '''
        Calculate new positions for well performing bees. Each bee that has performed better then
        average is combined with another well performing bee to move to a more optimal location. A
        location is a combination of values, the more optimal, the better that set of values will
        perform given the fitness function. If the new position performs better than the bee's current
        position, the bee will move to the new location
        '''
        self.__verify_ready()
        self._logger.log('debug',"Onlooker bee phase")
        modified = []
        for _ in self._employers:
            chosen_bee = np.random.choice(self._employers, p = [e.probability for e in self._employers])
            if self._processes <= 1:
                new_values = self._merge_bee(chosen_bee)
                self._move_bee(chosen_bee, new_values)
                self.__update(chosen_bee.score, chosen_bee.values, chosen_bee.error)
            else:
                modified.append((
                    chosen_bee,
                    self._pool.apply_async(self._merge_bee, [chosen_bee])
                ))
        for pair in modified:
            self._move_bee(pair[0], pair[1].get())
            self.__update(pair[0].score, pair[0].values, pair[0].error)
                    
    def _calc_probability(self):
        '''
        Calculate the average of bee cost. Will also update the best score and keep track of total score for probability
        '''
        self._logger.log('debug', "calculating total")
        self.__verify_ready()
        self._total_score = 0
        for employer in self._employers:
            self._total_score += employer.score
            # While iterating through employers, look for the best fitness score/value pairing
            if self.__update(employer.score, employer.values, employer.error):
                self._logger.log('info', "Best score update to error: {} | score: {} | values: {}".format(employer.error, employer.score, employer.values))

        # Now calculate each bee's probability
        for employer in self._employers:
            employer.calculate_probability(self._total_score)

    def _check_positions(self):
        '''
        Check the fitness cost of every bee to the average. If below average, and that bee has been reassigned
        a food source more than the allowed amount, assign that bee a new random set of values. Additionally, group
        together well performing bees. If score is better than current best, set is as current best
        '''
        self.__verify_ready()
        max_trials = 0
        scout = None
        for bee in self._employers:
            if (bee.failed_trials >= max_trials):
                max_trials = bee.failed_trials
                scout = bee
        if scout != None and scout.failed_trials > self._limit:
            self._logger.log('debug', "Sending scout (error of {} with limit of {})".format(scout.error, scout.failed_trials))
            scout.values = self. __gen_random_values()
            if self._processes <= 1:
                scout.score = scout.get_score(self._fitness_fxn(scout.values, **self._args))
                scout.failed_trials = 0
                self.__update(scout.score, scout.values, scout.error)
            else:
                scout.score = self._pool.apply_async(self._fitness_fxn, [scout.values], self._args)
                scout.failed_trials = 0
                try:
                    scout.get_score(scout.score.get())
                    self.__update(scout.score, scout.values, scout.error)
                except Exception as e:
                    raise e

    def import_settings(self, filename):
        '''
        Import settings from a JSON file
        '''
        if not os.path.isfile(filename):
            self._logger.log('error', "file: {} not found, continuing with default settings".format(filename))
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
        '''
        Save settings to a JSON file
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

    def _merge_bee(self, bee):
        '''
        Merge bee at self._to_modify[bee_index] with a well
        performing bee. Should not be called by user. Method
        cannot be self.__merge_bee to ensure that the method
        is pickled when multiprocessing is enabled
        '''
        # choose random dimension
        random_dimension = randint(0, len(self._value_ranges) - 1)
        # choose random 2nd bee
        second_bee = randint(0, self._num_employers-1)
        # Avoid both bees being the same
        while (bee.id == self._employers[second_bee].id):
            second_bee = randint(0, self._num_employers -1)
        # bee[dimension] = bee[dimension] + rand(-1, 1) * (rand_bee[dimension] - bee[dimension])
        new_bee = deepcopy(bee)
        new_bee.values[random_dimension] = self.__onlooker.calculate_positions(new_bee.values[random_dimension],
            self._employers[second_bee].values[random_dimension], self._value_ranges[random_dimension])
        fitness_score = new_bee.get_score(self._fitness_fxn(new_bee.values, **self._args))
        return (fitness_score, new_bee.values, new_bee.error)

    def __update(self, score, values, error):
        '''
        Update the best score and values if the given
        score is better than the current best score
        '''
        if self._minimize:
            if self._best_score == None or score < self._best_score:
                self._best_score = score
                self._best_values = values.copy()
                self._best_error = error
                self._logger.log('debug','New best food source memorized: {}'.format(self._best_error))
                return True
        elif not self._minimize:
            if self._best_score == None or score > self._best_score:
                self._best_score = score
                self._best_values = values.copy()
                self._best_error = error
                self._logger.log('debug','New best food source memorized: {}'.format(self._best_error))
                return True
        return False

    def __gen_random_values(self):
        '''
        Generate a random list of values based on the allowed value ranges
        '''
        values = []
        if self._value_ranges == None:
            self._logger.log('crit', "must set the type/range of possible values")
            raise RuntimeError("must set the type/range of possible values")
        else:
            # t[0] contains the type of the value, t[1] contains a tuple (min_value, max_value)
            for t in self._value_ranges:
                if t[0] == 'int':
                    values.append(randint(t[1][0], t[1][1]))
                elif t[0] == 'float':
                    values.append(np.random.uniform(t[1][0], t[1][1]))
                else:
                    self._logger.log('crit', "value type must be either an 'int' or a 'float'")
                    raise RuntimeError("value type must be either an 'int' or a 'float'")
        return values

    def __verify_ready(self, creating=False):
        '''
        Some cleanup, ensures that everything is set up properly to avoid random
        errors during execution
        '''
        if len(self._value_ranges) == 0:
            self._logger.log('crit', 'Attribute value_ranges must have at least one value')
            raise RuntimeWarning('Attribute value_ranges must have at least one value')
        if len(self._employers) == 0 and creating == False:
            self._logger.log('crit', "Need to create employers")
            raise RuntimeWarning("Need to create employers")

    def __getstate__(self):
        '''
        Returns appropriate dictionary for correctly
        pickling the ABC object in case of multiprocssing
        '''
        state = self.__dict__.copy()
        del state['_logger']
        del state['_pool']
        return state
