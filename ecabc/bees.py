#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/bees.py
#  v.2.0.3
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program defines the bee objects created in the artificial bee colony
#

import numpy as np
from random import randint

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

    def calculate_probability(self, fitness_average):
        '''
        Calculate probability based on a given fitness average
        '''
        self.probability = self.score / fitness_average

    def get_fitness_score(self, values, fitness_function):
        '''
        Get fitness score for a given set of values
        '''
        score = fitness_function(values)  
        if self.score == None or score < self.score:
            self.value = values
            self.score = score

class OnlookerBee:
    '''
    Class to store best performing bees, and also
    calculate positions for any given bees
    '''

    def __init__(self):
        self.best_employers = []
    
    def calculate_positions(self, first_bee, second_bee, value_types):
        '''
        Calculate the positions when merging two bees
        '''
        new_values = first_bee.values
        index = randint(0, len(first_bee.values)-1)
        value = self.__value_function(first_bee.values[index], second_bee.values[index])
        if value_types[index] == 'int':
            value = int(value)
        new_values[index] = value
        return new_values

    def __value_function(self, a, b):  
        '''
        Algorithm used to merge the same value type from two
        different bees
        '''
        activationNum = np.random.uniform(-1, 1)
        return a + abs(activationNum * (a - b))
