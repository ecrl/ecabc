#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/bees.py
#  v.2.0.0
#  Developed in 2018 by Sanskriti Sharma <Sanskriti_Sharma@student.uml.edu> and Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program defines the bee objects created in the artificial bee colony
#

import numpy as np
from random import randint

### Bee object, employers contain value/fitness
class Bee:
    
    def __init__(self, values=[]):
        self.values = values            
        self.score = None

    ### Onlooker bee function, create a new set of positions
    def calculate_positions(self, first_bee, second_bee, value_types):
        new_values = first_bee.values
        index = randint(0, len(first_bee.values)-1)
        value = self.__value_function(first_bee.values[index], second_bee.values[index]) #why is this a separate function??
        if value_types[index] == 'int':
            value = int(value)
        new_values[index] = value
        return new_values

    def calculate_fitness(self, error):
        if error >= 0:
            self.fitness = 1/(error+1)
        else:
            self.fitness = 1 + abs(error)

    #### Employer bee function, get fitness score for a given set of values
    def get_fitness_score(self, values, fitness_function):
        score = fitness_function(values)  
        if self.score == None or score < self.score:
            self.value = values
            self.score = score

    ### Method of generating a value in between the values given
    def __value_function(self, a, b):  
        activationNum = np.random.uniform(-1, 1)
        return a + abs(activationNum * (a - b))

class employedBee(Bee):
    def __init__(self):
		self.probability = 0

