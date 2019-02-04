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

    def update(self, error):
        self.error = error
        if self.error >= 0:
            self.score = 1/(self.error+1)
        else:
            self.score = 1 + abs (self.error)

    def calculate_probability(self, fitness_total):
        '''
        Calculate probability based on a given fitness average
        '''
        self.probability = self.score / fitness_total        

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
