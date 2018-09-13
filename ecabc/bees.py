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
    
    def __init__(self, beeType, values=[]):
        self.beeType = beeType
        # Only onlooker bees should store best performing employers
        if beeType == 'onlooker':
            self.bestEmployers = []
        # Only the employer bees should store values/fitness scores
        elif beeType == "employer":               
            self.values = values            
            self.currFitnessScore = None

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
        if self.beeType != "employer":
            raise RuntimeError("Cannot get fitness score on a non-employer bee")
        else:
            # Your fitness function must take a certain set of values that you would like to optimize
            fitnessScore = fitnessFunction(values)  
            if self.currFitnessScore == None or fitnessScore < self.currFitnessScore:
                self.value = values
                self.currFitnessScore = fitnessScore

    ### Method of generating a value in between the values given
    def valueFunction(self, a, b):  
        activationNum = np.random.uniform(-1, 1)
        return a + abs(activationNum * (a - b))
