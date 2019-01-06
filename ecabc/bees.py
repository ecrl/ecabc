#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/bees.py
#  v.2.1.1
#  Developed in 2018 by Sanskriti Sharma <sanskriti_sharma@student.uml.edu> & Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program defines the bee objects created in the artificial bee colony
#

import numpy as np
from random import randint

import uuid

class EmployerBee:

    '''
    Class which stores individual employer bee information. A probability it will get picked, a score
    and the values that pertain to the score
    '''

    def __init__(self, values=[]):
        self.values = values
        self.score = None
        self.probability = 0
        self.failed_trials = 0
        self.id = uuid.uuid4()
        self.error = None

    def calculate_probability(self, fitness_total):
        '''
        Calculate probability based on a given fitness average
        '''
        self.probability = self.score / fitness_total

    def get_fitness_score(self, fitness_fxn, values):
        '''
        Get fitness score for a given set of values
        '''
        self.error = fitness_fxn(self.values, values)
        print(str(self.error) + " maps to " + str(1/(self.error + 1)))
        if self.error >= 0:
            return 1/(self.error+1)
        else:
            return 1 + abs (self.error)

class OnlookerBee:
    '''
    Class to store best performing bees, and also
    calculate positions for any given bees
    '''

    def __init__(self):
        self.best_employers = []

    def calculate_positions(self, first_bee_val, second_bee_val, value_range):
        '''
        Calculate the positions when merging two bees
        '''
        value = first_bee_val + np.random.uniform(-1, 1) \
                * (first_bee_val - second_bee_val)
        if value_range[0] == 'int': value = int(value)
        if value > value_range[1][1]: value = value_range[1][1] 
        if value < value_range[1][0]: value = value_range[1][0]

        return value
