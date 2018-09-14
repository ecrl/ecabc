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
import logging
from multiprocessing import Pool

# artificial bee colony packages
from ecabc.bees import Bee
from ecabc.settings import Settings
from ecabc.logger import Logger

### Artificial bee colony object, which contains multiple bee objects ###
class ABC:

    def __init__(self, value_ranges, fitness_fxn, print_level=logging.INFO, file_logging=False, processes=5):
        self.__logger = Logger(print_level, file_logging, 'abc_logger')
        self.__value_ranges = value_ranges
        self.__fitness_fxn = fitness_fxn
        self.__onlooker = Bee('onlooker')
        self.__processes = processes
        self.__pool = Pool(processes)
        self.__saving = None
        self.__settings = None
        self.__employers = []
     
    ### Assign a new position to the given bee
    def calc_new_positions(self):
        self.__verify_ready()
        modified_bees = []
        for i in range(len(self.__onlooker.best_employers)):
            valueTypes = [t[0] for t in self.__settings._valueRanges]
            secondBee = randint(0, len(self.__onlooker.best_employers) -1)
            # Avoid both bees being the same
            while (secondBee == i):
                secondBee = randint(0, len(self.__onlooker.best_employers) -1)
            positions = self.__onlooker.calculate_positions(self.__onlooker.best_employers[i], self.__onlooker.best_employers[secondBee], valueTypes)
            self.__onlooker.best_employers[i].score = positions
            # If multi processing
            if self.__processes > 0:
                try:
                    self.__onlooker.best_employers[i].score = self.__pool.apply_async(self.__fitness_fxn, [positions])
                    modified_bees.append(self.__onlooker.best_employers[i])
                except Exception as e:
                    raise e
            # No multi processing
            else:
                self.__onlooker.best_employers[i].score = self.__fitness_fxn(positions)
                self.__logger.debug("Assigned new position to {}/{}".format(i+1, len(self.__onlooker.best_employers)))
        if self.__processes > 0:
            for i in range(len(modified_bees)):
                modified_bees[i].score = modified_bees[i].score.get()
                self.__logger.debug("Assigned new position to {}/{}".format(i+1, len(self.__onlooker.best_employers)))
    
    ### Collect the average fitness score across all employers
    def calc_average(self):
        self.__verify_ready()
        self.__average_score = 0
        for employer in self.__employers:
            self.__average_score += employer.score
            # While iterating through employers, look for the best fitness score/value pairing
            if self.__settings.update(employer.score, employer.values):
                self.__logger.info("Best score update to score: {} | values: {}".format(employer.score, employer.values)) 
        self.__average_score /= len(self.__employers)
    
    def get_average(self):
        return self.__average_score
    
    ### Iterate through all bees to see if their positions are below average, assign them new values if they are
    def check_positions(self):
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
                        self.__logger.info("Best score update to score: {} | values: {} ".format(bee.score, bee.values))
                except Exception as e:
                    raise e
        # No multiprocessing
        else:
            for bee in self.__employers:
                if self.__below_average(bee):
                    bee.values = self.__gen_random_values()
                    bee.score = self.__fitness_fxn(bee.values)
                    if self.__settings.update(bee.score, bee.values):
                        self.__logger.info("Best score update to score: {} | values: {} ".format(bee.score, bee.values))

    ### Return a tuple, best score - best values pair
    def get_best_performer(self):
        return self.__settings.get_best()

    ### Import settings from a file
    def import_settings(self, filename):
        try:
            self.__settings.import_settings(filename)
            return True
        except FileNotFoundError:
            self.__logger.error("file: {} not found, continuing with default settings")
            self.__settings = Settings(self.__value_ranges, 50)
            return False

    ### Save all current settings/scores
    def save_settings(self, filename):
        self.__settings.save_settings(filename)
    
    ### Create employer bees
    def create_employers(self):
        self.__verify_ready(True)
        num_employers = self.__settings._num_employers
        # If multiprocessing
        if self.__processes > 0:
            for i in range(num_employers):
                self.__employers.append(Bee('employer', self.__gen_random_values()))
                self.__employers[i].score = self.__pool.apply_async(self.__fitness_fxn, [self.__employers[i].values])
            for i in range(num_employers):
                try:
                    self.__employers[i].score = self.__employers[i].score.get()
                    self.__logger.debug("Bee number {} created".format(i+1))
                except Exception as e:
                    raise e
        # No multiprocessing
        else:
            for i in range(num_employers):
                self.__employers.append(Bee('employer', self.__gen_random_values()))
                self.__employers[i].score = self.__fitness_fxn(self.__employers[i].values)
                self.__logger.debug("Bee number {} created".format(i+1))
    
    ### Specify whether the artificial bee colony will maximize or minimize the fitness cost
    def minimize(self, minimize):
        self.__settings._minimize = minimize
        
    ### Return whether the bee has a fitness score worse than the average
    def __below_average(self, bee):
        return (self.__settings._minimize == True and bee.score  > self.__average_score) or\
               (self.__settings._minimize == False and bee.score < self.__average_score)

    ### Generate a random set of values given a value range
    def __gen_random_values(self):
        values = []
        if self.__settings._valueRanges == None:
            self.__logger.fatal("must set the type/range of possible values")
            raise RuntimeError("must set the type/range of possible values")
        else:
            # t[0] contains the type of the value, t[1] contains a tuple (min_value, max_value)
            for t in self.__settings._valueRanges:  
                if t[0] == 'int':
                    values.append(randint(t[1][0], t[1][1]))
                elif t[0] == 'float':
                    values.append(np.random.uniform(t[1][0], t[1][1]))
                else:
                    self.__logger.fatal("value type must be either an 'int' or a 'float'")
                    raise RuntimeError("value type must be either an 'int' or a 'float'")
        return values

    ### Check that you have created employers
    def __verify_ready(self, creating=False):
        if len(self.__employers) == 0 and creating == False:
            self.__logger.fatal("Need to create employers")
            raise RuntimeWarning("Need to create employers")
        elif not self.__settings:
            self.__settings = Settings(self.__value_ranges, 50)

    ### Some miscellaneous cleanup
    def __del__(self):
        if self.__processes > 0:
            self.__logger.debug("Object being destroyed, joining and closing pool")
            self.__pool.join()
            self.__pool.close()
    