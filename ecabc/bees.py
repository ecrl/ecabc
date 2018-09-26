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
    
    def __init__(self, bee_type, values=[]):
        self.bee_type = bee_type
        # Only onlooker bees should store best performing employers
        if bee_type == 'onlooker':
            self.best_employers = []
        # Only the employer bees should store values/fitness scores
        elif bee_type == "employer":               
            self.values = values            
            self.score = None

    ### Onlooker bee function, create a new set of positions
    def calculate_positions(self, first_bee, second_bee, value_types):
        new_values = first_bee.values
        index = randint(0, len(first_bee.values)-1)
        value = self.__value_function(first_bee.values[index], second_bee.values[index])
        if value_types[index] == 'int':
            value = int(value)
        new_values[index] = value
        return new_values

    #### Employer bee function, get fitness score for a given set of values
    def get_fitness_score(self, values, fitness_function):
        if self.bee_type != "employer":
            raise RuntimeError("Cannot get fitness score on a non-employer bee")
        else:
            # Your fitness function must take a certain set of values that you would like to optimize
            score = fitness_function(values)  
            if self.score == None or score < self.score:
                self.value = values
                self.score = score

    ### Method of generating a value in between the values given
    def __value_function(self, a, b):  
        activationNum = np.random.uniform(-1, 1)
        return a + abs(activationNum * (a - b))
