#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.2.0.0
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program implements an artificial bee colony to tune ecnet hyperparameters
#

import sys as sys
from random import randint
import numpy as np
from colorlogging import ColorLogger
from multiprocessing import Pool

# artificial bee colony packages
from ecabc.bees import *
from ecabc.settings import Settings


class ABC:
    
    '''
    ABC object: Manages employer and onlooker bees to optimize a set of generic values 
    given a generic user defined fitness function. Handles data transfer and manipulation 
    between bees.
    '''

    def __init__(self, value_ranges, fitness_fxn, print_level='info', file_logging='disable', processes=5):
        self.__logger = ColorLogger(stream_level=print_level, file_level=file_logging)
        self.__value_ranges = value_ranges
        self.__fitness_fxn = fitness_fxn
        self.__onlooker = OnlookerBee()
        self.__processes = processes
        if processes > 0:
            self.__pool = Pool(processes)
        self.__saving = None
        self.__settings = None
        self.__employers = []

    def create_employers(self):
        '''
        Generate a set of employer bees. This method must be called in order to generate a set
        of usable employers bees. Other methods depend on this.
        '''
        self.__verify_ready(True)
        num_employers = self.__settings._num_employers
        # If multiprocessing
        if self.__processes > 0:
            for i in range(num_employers):
                self.__employers.append(EmployerBee(self.__gen_random_values()))
                self.__employers[i].score = self.__pool.apply_async(self.__fitness_fxn, [self.__employers[i].values])
            for i in range(num_employers):
                try:
                    self.__employers[i].score = self.__employers[i].score.get()
                    self.__logger.log('debug', "Bee number {} created".format(i+1))
                except Exception as e:
                    raise e
        # No multiprocessing
        else:
            for i in range(num_employers):
                self.__employers.append(EmployerBee(self.__gen_random_values()))
                self.__employers[i].score = self.__fitness_fxn(self.__employers[i].values)
                self.__logger.log('debug', "Bee number {} created".format(i+1))
     
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
        self.__logger.log('debug', "probability is {}".format(probability))
        for i in range(len(self.__onlooker.best_employers)):
            self.__onlooker.best_employers[i].calculate_probability(self.__average_score)
            if self.__onlooker.best_employers[i].probability >= probability:
                valueTypes = [t[0] for t in self.__settings._valueRanges]
                secondBee = randint(0, len(self.__onlooker.best_employers) -1)
                # Avoid both bees being the same
                while (secondBee == i):
                    secondBee = randint(0, len(self.__onlooker.best_employers) -1)
                positions = self.__onlooker.calculate_positions(self.__onlooker.best_employers[i], self.__onlooker.best_employers[secondBee], valueTypes)
                new_score = self.__fitness_fxn(positions)
                if self.__is_better(new_score, self.__onlooker.best_employers[i].score):
                    self.__onlooker.best_employers[i].values = positions
                    self.__onlooker.best_employers[i].score = new_score
                    self.__logger.log('debug', "Assigned new position to {}/{}".format(i+1, len(self.__onlooker.best_employers)))
    
    def calc_average(self):
        '''
        Calculate the average of bee cost. Will also update the best score
        '''
        self.__verify_ready()
        self.__average_score = 0
        for employer in self.__employers:
            self.__average_score += employer.score
            # While iterating through employers, look for the best fitness score/value pairing
            if self.__settings.update(employer.score, employer.values):
                self.__logger.log('info', "Best score update to score: {} | values: {}".format(employer.score, employer.values)) 
        self.__average_score /= len(self.__employers)

        # Now calculate each bee's probability
        self.__gen_probability_values()
    
    def get_average(self):
        return self.__average_score
    
    def check_positions(self):
        '''
        Check the fitness cost of every bee to the average. If below average, assign that bee a new random
        set of values. Additionally, group together well performing bees. If score is better than current 
        best, set is as current best
        '''
        self.__verify_ready()
        self.__onlooker.best_employers = []
        # If multi processing
        if self.__processes > 0:
            modified_bees = []
            for bee in self.__employers:
                if self.__below_average(bee):
                    bee.values = self.__gen_random_values()
                    bee.score = self.__pool.apply_async(self.__fitness_fxn, [bee.values])
                    modified_bees.append(bee)
                else:
                    # Assign the well performing bees to the onlooker
                    self.__onlooker.best_employers.append(bee)
            for bee in modified_bees:
                try:
                    bee.score = bee.score.get()
                    if self.__settings.update(bee.score, bee.values):
                        self.__logger.log('info', "Best score update to score: {} | values: {} ".format(bee.score, bee.values))
                except Exception as e:
                    raise e
        # No multiprocessing
        else:
            for bee in self.__employers:
                if self.__below_average(bee):
                    bee.values = self.__gen_random_values()
                    bee.score = self.__fitness_fxn(bee.values)
                    if self.__settings.update(bee.score, bee.values):
                        self.__logger.log('info', "Best score update to score: {} | values: {} ".format(bee.score, bee.values))
                else:
                    self.__onlooker.best_employers.append(bee)

    def get_best_performer(self):
        '''
        Get the best performing bee
        '''
        return self.__settings.get_best()

    def import_settings(self, filename):
        try:
            self.__settings.import_settings(filename)
            return True
        except FileNotFoundError:
            self.__logger.log('error', "file: {} not found, continuing with default settings")
            self.__settings = Settings(self.__value_ranges, 50)
            return False

    def save_settings(self, filename):
        self.__settings.save_settings(filename)
    
    def minimize(self, minimize):
        self.__settings._minimize = minimize
        
    def __below_average(self, bee):
        return (self.__settings._minimize == True and bee.score  > self.__average_score) or\
               (self.__settings._minimize == False and bee.score < self.__average_score)
    
    def __is_better(self, first_score, comparison):
        return (self.__settings._minimize == True and first_score  < comparison) or\
               (self.__settings._minimize == False and first_score > comparison)

    def __gen_random_values(self):
        '''
        Generate a random list of values based on the allowed value ranges
        '''
        values = []
        if self.__settings._valueRanges == None:
            self.__logger.log('fata', "must set the type/range of possible values")
            raise RuntimeError("must set the type/range of possible values")
        else:
            # t[0] contains the type of the value, t[1] contains a tuple (min_value, max_value)
            for t in self.__settings._valueRanges:  
                if t[0] == 'int':
                    values.append(randint(t[1][0], t[1][1]))
                elif t[0] == 'float':
                    values.append(np.random.uniform(t[1][0], t[1][1]))
                else:
                    self.__logger.log('fata', "value type must be either an 'int' or a 'float'")
                    raise RuntimeError("value type must be either an 'int' or a 'float'")
        return values

    def __gen_probability_values(self):
        for employer in self.__employers:
            employer.calculate_probability

    def __verify_ready(self, creating=False):
        '''
        Some cleanup, ensures that everything is set up properly to avoid random 
        errors during execution
        '''
        if len(self.__employers) == 0 and creating == False:
            self.__logger.log('fatal', "Need to create employers")
            raise RuntimeWarning("Need to create employers")
        elif not self.__settings:
            self.__settings = Settings(self.__value_ranges, 50)

