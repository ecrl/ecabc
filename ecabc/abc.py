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

    def __init__(self, valueRanges, fitnessFunction=None, endValue=None, iterationAmount=None,\
     amountOfEmployers=50, filename='settings.json', printLevel=logging.INFO, file_logging=False, 
     importing=False, processes=5):
        self.__logger = Logger(printLevel, file_logging, 'abc_logger')
        if endValue == None and iterationAmount == None:
            self.__logger.fatal("must select either an iterationAmount or and endValue")
            raise ValueError("must select either an iterationAmount or and endValue")
        if fitnessFunction == None:
            self.__logger.fatal("must pass a fitness function")
            raise ValueError("must pass a fitness function")
        self.saving = filename is not None
        self.__iteration_count = 0
        self.__settings = Settings(valueRanges, iterationAmount, endValue, amountOfEmployers, filename, processes)
        if self.saving:
            if importing:
                try:
                    self.__settings.importSettings()
                    self.__logger.debug("Imported file {}".format(filename))
                except FileNotFoundError:
                    self.__logger.debug("Creating new settings file")
                self.__settings.saveSettings()
                self.__logger.debug("Settings saved'")
            else:
                self.__settings.saveSettings()
                self.__logger.debug("Settings saved'")
        if self.__settings._processes > 0:
            self.__logger.debug("Creating {} processes".format(self.__settings._processes))
            self.__pool = Pool(processes)
        self.__fitness_fxn = fitnessFunction
        self.__employers = []
        self.__onlooker = Bee('onlooker')
        self.__average_score = 0
        # Initialize employer bees, assign them values/fitness scores
        self.__logger.debug("***INITIALIZING ABC***")
        self.__create_employers(amountOfEmployers)
        self.__logger.debug("***DONE INITIALIZING***")
     
    ### Assign a new position to the given bee
    def assignNewPositions(self, firstBee):
        valueTypes = [t[0] for t in self.__settings._valueRanges]
        secondBee = randint(0, len(self.__employers) -1)
        # Avoid both bees being the same
        while (secondBee == firstBee):
            secondBee = randint(0, len(self.__onlooker.bestEmployers) -1)
        self.__onlooker.getPosition(self.__employers, firstBee, secondBee, self.__fitness_fxn, valueTypes)
    
    ### Collect the average fitness score across all employers
    def getFitnessAverage(self):
        self.__average_score = 0
        for employer in self.__employers:
            self.__average_score += employer.score
            # While iterating through employers, look for the best fitness score/value pairing
            if self.__settings.update(employer.score, employer.values):
                self.__logger.info("Best score update to score: {} | values: {}".format(employer.score, employer.values)) 
        self.__average_score /= len(self.__employers)

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
    
    ### Check if new position is better than current position held by a bee
    def checkNewPositions(self):
        # If multi processing
        if self.__settings._processes > 0:
            modified_bees = []
            for bee in self.__employers:
                if self.__below_average(bee):
                    bee.values = self.__gen_random_values()
                    bee.score = self.__pool.apply_async(self.__fitness_fxn, [bee.values])
                    modified_bees.append(bee)
                else:
                    # Assign the well performing bees to the onlooker
                    self.__onlooker.bestEmployers.append(bee)
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

    ### If termination depends on a target value, check to see if it has been reached
    def checkIfDone(self, count):
        stop = False
        if self.__settings._endValue != None:
            if self.betterThanEndValue(self.__settings._bestScore):
                stop = True
        elif count >= self.__settings._iterationAmount:
            stop = True
        return stop

    ### Set the amount of processes that can run at a time
    def set_process_limit(self, process_limit):
        self.__settings.set_process_limit(process_limit)

    ### Return a tuple, best score - best values pair
    def get_best_performer(self):
        return self.__settings.get_best()

    ### Import settings from a file
    def import_settings(self, filename):
        try:
            self.__settings.importSettings()
        except FileNotFoundError:
            self.__logger.error("file: {} not found, continuing with default settings")
            ### TODO ###

    ### Save all current settings/scores
    def save_settings(self):
        self.__settings.saveSettings()
    
    ### Create employer bees
    def __create_employers(self, amountOfEmployers):
        # If multiprocessing
        if self.__settings._processes > 0:
            for i in range(amountOfEmployers):
                self.__employers.append(Bee('employer', self.__gen_random_values()))
                self.__employers[i].score = self.__pool.apply_async(self.__fitness_fxn, [self.__employers[i].values])
            for i in range(amountOfEmployers):
                try:
                    self.__employers[i].score = self.__employers[i].score.get()
                    self.__logger.debug("Bee number {} created".format(i+1))
                except Exception as e:
                    raise e

        # No multiprocessing
        else:
            for i in range(amountOfEmployers):
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
    
    ### Return whether the bee's fitness score hits the specified end value
    def betterThanEndValue(self, score):
        return (self.__settings._minimize == True and score <= self.__settings._endValue) or\
               (self.__settings._minimize == False and score >= self.__settings._endValue)

    ### Run the artificial bee colony
    def runABC(self):

        while True:
            
            self.__onlooker.bestEmployers.clear()
            self.__logger.debug("Assigning new positions")
            for i in range(len(self.__onlooker.bestEmployers)):
                self.__logger.debug('At bee number: %d \r' % (i+1))
                self.assignNewPositions(i)
            self.__logger.debug("Getting fitness average")
            self.getFitnessAverage()
            self.__logger.info("Current fitness average: {}".format(self.__average_score))
            if self.__settings._iterationAmount != None:
                self.__logger.debug("Iteration {} / {}".format(self.__iteration_count+1, self.__settings._iterationAmount))
            self.__iteration_count+=1

            self.__logger.debug("Checking if done")
            if self.saving:
                self.__logger.debug("Saving settings")
                self.__settings.saveSettings()
            if self.checkIfDone(self.__iteration_count):
                break

            self.__logger.debug("Checking new positions, assigning random positions to bad ones")
            self.checkNewPositions()
            self.__logger.info("Best score: {}".format(self.__settings._bestScore))
            self.__logger.info("Best value: {}".format(self.__settings._bestValues))

        if self.__settings._processes > 0:
            self.__pool.close()
            self.__pool.join()
            self.__logger.debug("Process pool closed")
        self.__logger.info("Run ABC finished. Score: {} | Values: {}".format(self.__settings._bestScore, self.__settings._bestValues))
        return self.__settings._bestValues
