#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/bees.py
#  v.2.0.0
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program defines the bee objects created in the artificial bee colony
#

import numpy as np

### Bee object, employers contain value/fitness
class Bee:
    
    def __init__(self, bee_type, values=[]):
        self.__bee_type = bee_type
        # Only onlooker bees should store best performing employers
        if bee_type == 'onlooker':
            self.bestEmployers = []
        # Only the employer bees should store values/fitness scores
        elif bee_type == "employer":               
            self.values = values            
            self.score = None

    ### Onlooker bee function, create a new set of positions
    def getPosition(self, beeList, firstBee, secondBee, fitnessFunction, valueTypes):
        newValues = []
        currValue = 0
        for i in range(len(valueTypes)):
            currValue = self.valueFunction(beeList[firstBee].values[i], beeList[secondBee].values[i])
            if valueTypes[i] == 'int':
                currValue = int(currValue)
            newValues.append(currValue)
        beeList[firstBee].getFitnessScore(newValues, fitnessFunction)

    #### Employer bee function, get fitness score for a given set of values
    def getFitnessScore(self, values, fitnessFunction):
        if self.__bee_type != "employer":
            raise RuntimeError("Cannot get fitness score on a non-employer bee")
        else:
            # Your fitness function must take a certain set of values that you would like to optimize
            fitnessScore = fitnessFunction(values)  
            if self.score == None or fitnessScore < self.score:
                self.value = values
                self.score = fitnessScore

    ### Method of generating a value in between the values given
    def valueFunction(self, a, b):  
        activationNum = np.random.uniform(-1, 1)
        return a + abs(activationNum * (a - b))
