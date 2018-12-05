#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.2.0.3
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program implements an artificial bee colony to tune ecnet hyperparameters
#

import sys as sys
import os.path
import json
from random import randint
import numpy as np
from colorlogging import ColorLogger
from multiprocessing import Pool

# artificial bee colony packages
from ecabc.bees import *


class ABC:
    
    '''
    ABC object: Manages employer and onlooker bees to optimize a set of generic values 
    given a generic user defined fitness function. Handles data transfer and manipulation 
    between bees.
    '''

    def __init__(self, value_ranges, fitness_fxn, print_level='info', file_logging='disable', processes=5):
        self._logger = ColorLogger(stream_level=print_level, file_level=file_logging)
        self._value_ranges = value_ranges
        self._num_employers = 50
        self._best_values = []
        self._best_score = None
        self._minimize = True
        self._fitness_fxn = fitness_fxn
        self._onlooker = OnlookerBee()
        self._processes = processes
        self._to_modify = []
        self._limit = 20
        self._processes = processes
        self._employers = []
        if processes > 0:
            self._pool = Pool(processes)
        else:
            self._pool = None

    @property 
    def minimize(self):
        return self._minimize

    @minimize.setter
    def minmize(self, minimize):
        self._minimize = minimize
        self._logger.log('debug', "Minimize set to {}".format(minimize))

    @property
    def num_employers(self):
        return self._num_employers
    
    @num_employers.setter
    def num_employers(self, num_employers):
        self._num_employers = num_employers
        self._logger.log('debug', "Number of employers set to {}".format(num_employers))

    @property 
    def processes(self):
        return self._processes

    @processes.setter
    def processes(self, processes):
        if self._processes > 0:
            self._pool.join()
            self._pool.close()

        self._processes = processes
        if self._processes > 0:
            self._pool = Pool(processes)
        else:
            self._pool = None
        self._logger.log('debug', "Number of processes set to {}".format(processes))

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
        Return a tuple (best_score, best_values)
        '''
        return (self._best_score, self._best_values)

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
        Set the maximum amoutn of times a bee can perform below average
        before completely bandoning its current food source and seeking 
        a randomly generate done
        '''
        self._limit = limit

    def create_employers(self):
        '''
        Generate a set of employer bees. This method must be called in order to generate a set
        of usable employers bees. Other methods depend on this.
        '''
        self.__verify_ready(True)
        # If multiprocessing
        for _ in range(self._num_employers):
            employer = EmployerBee(self.__gen_random_values())
            if self._processes > 0:
                employer.score = self._pool.apply_async(self._fitness_fxn, [employer.values])
            else:
                employer.score = self._fitness_fxn(employer.values)
            self._employers.append(employer)
        if self._processes > 0:
            for i, employer in enumerate(self._employers):
                try:
                    employer.score = employer.score.get()
                    self._logger.log('debug', "Bee number {} created".format(i + 1))
                except Exception as e:
                    raise e
     
    def calc_new_positions(self):
        '''
        Calculate new positions for well performing bees. Each bee that has performed better then
        average is combined with another well performing bee to move to a more optimal location. A 
        location is a combination of values, the more optimal, the better that set of values will 
        perform given the fitness function. If the new position performs better than the bee's current
        position, the bee will move to the new location
        '''
        self.__verify_ready()
        probability = np.random.uniform(0,1)
        for i, bee in enumerate(self._to_modify):
            if bee.probability >= probability:
                new_values = self.__merge_bee(i)
                if self.__is_better(bee.score, new_values[0]):
                    bee.failed_trials += 1
                else:
                    bee.score = new_values[0]
                    bee.values = new_values[1]
                    bee.failed_trials = 0
                    self._logger.log('debug', "Bee assigned to new merged position")

    def calc_average(self):
        '''
        Calculate the average of bee cost. Will also update the best score
        '''
        self._logger.log('debug', "calculating average")
        self.__verify_ready()
        self._average_score = 0
        for employer in self._employers:
            self._average_score += employer.score
            # While iterating through employers, look for the best fitness score/value pairing
            if self.__update(employer.score, employer.values):
                self._logger.log('info', "Best score update to score: {} | values: {}".format(employer.score, employer.values)) 
        self._average_score /= len(self._employers)

        # Now calculate each bee's probability
        self.__gen_probability_values()
    
    def check_positions(self):
        '''
        Check the fitness cost of every bee to the average. If below average, and that bee has been reassigned
        a food source more than the allowed amount, assign that bee a new random set of values. Additionally, group 
        together well performing bees. If score is better than current best, set is as current best
        '''
        self.__verify_ready()
        self._onlooker.best_employers = []
        self._to_modify = []
        modified_bees = []

        for bee in self._employers:
            if bee.failed_trials >= self._limit:
                bee.values = self.__gen_random_values()
                # Check whether multiprocessing is enabled
                if self._processes > 0:
                    bee.score = self._pool.apply_async(self._fitness_fxn, [bee.values])
                else:
                    bee.score = self._fitness_fxn(bee.values)
                bee.failed_trials = 0
                modified_bees.append(bee)
            else:
                # Assign the well performing bees to the onlooker
                if not self.__below_average(bee):
                    self._onlooker.best_employers.append(bee)
                self._to_modify.append(bee)
        # Wait for all the bee values to be calculated if multiprocessing is enabled
        if self._processes > 0:
            for bee in modified_bees:
                try:
                    bee.score = bee.score.get()
                    self._logger.log('debug', "Generated new random bee score")
                    if self.__update(bee.score, bee.values):
                        self._logger.log('info', "Best score update to score: {} | values: {} ".format(bee.score, bee.values))
                except Exception as e:
                    raise e

    def import_settings(self, filename):
        '''
        Import settings from a JSON file
        '''
        if not os.path.isfile(filename):
            self._logger.log('error', "file: {} not found, continuing with default settings".format(filename))
            raise FileNotFoundError('could not open setting file')
        else:
            with open(filename, 'r') as jsonFile:
                data = json.load(jsonFile)
                self._value_ranges = data['valueRanges']
                self._best_values = data['best_values']
                self._minimize = data['minimize']
                self._num_employers = data['num_employers']
                self._best_score = data['best_score']

    def save_settings(self, filename):
        data = dict()
        data['valueRanges'] = self._value_ranges
        data['best_values'] = self._best_values
        data['minimize'] = self._minimize
        data['num_employers'] = self._num_employers
        data['best_score'] = self._best_score
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

    def __merge_bee(self, bee_index):
        valueTypes = [t[0] for t in self._value_ranges]
        secondBee = randint(0, len(self._onlooker.best_employers) - 1)
        positions = self._onlooker.calculate_positions(self._to_modify[bee_index],
            self._onlooker.best_employers[secondBee], valueTypes)
        new_score = self._fitness_fxn(positions)
        return (new_score, positions)

    def __below_average(self, bee):
        return (self._minimize == True and bee.score  > self._average_score) or\
               (self._minimize == False and bee.score < self._average_score)
    
    def __is_better(self, first_score, comparison):
        return (self._minimize == True and first_score  < comparison) or\
               (self._minimize == False and first_score > comparison)

    def __update(self, score, values):
        if self._minimize: 
            if self._best_score == None or score < self._best_score:
                self._best_score = score
                self._best_values = values
                return True
        elif not self._minimize:
            if self._best_score == None or score > self._best_score:
                self._best_score = score
                self._best_values = values
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

    def __gen_probability_values(self):
        for employer in self._employers:
            employer.calculate_probability(self._average_score)

    def __verify_ready(self, creating=False):
        '''
        Some cleanup, ensures that everything is set up properly to avoid random 
        errors during execution
        '''
        if len(self._employers) == 0 and creating == False:
            self._logger.log('crit', "Need to create employers")
            raise RuntimeWarning("Need to create employers")

