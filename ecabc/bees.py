#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/bees.py
#  v.1.0.4.dev2
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program defines the bee objects created in the artificial bee colony
#

# artificial bee colony program import
from ecabc.helper_functions import valueFunction

### Bee object, employers contain value/fitness
class Bee:
    
    def __init__(self, beeType, values=[]):
        self.beeType = beeType
        # Only the employer bees should store values/fitness scores
        if beeType == "employer":               
            self.values = values            
            self.currFitnessScore = None

    ### Onlooker bee function, create a new set of positions
    def getPosition(self, beeList, firstBee, secondBee, fitnessFunction, valueTypes):
        newValues = []
        currValue = 0
        for i in range(len(valueTypes)):
            currValue = valueFunction(beeList[firstBee].values[i], beeList[secondBee].values[i])
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
