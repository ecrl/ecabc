from ecnet.server import Server
from random import *
import numpy as np
from BeeFunctions import *


class Bee:
    def __init__(self, beeType, values=[]):

        self.beeType = beeType
        self.values = values
        self.currFitnessScore = 100000

    '''Onlooker Bee Functions'''

    def getPosition(self, beeList, firstBee, secondBee):
        newValues = []
        currValue = 0

        for i in range(6):
            currValue = valueFunction(beeList[firstBee].values[i], beeList[secondBee].values[i])
            newValues.append(currValue)

        beeList[firstBee].getFitnessScore(newValues)

    '''Scout Bee Function'''

    def findRandomLocation(self):
        values = generateRandomValues()
        return values

    '''Employer Bee Functions'''

    def getFitnessScore(self, values):
        fitnessScore = runNeuralNet(values)
        if fitnessScore < self.currFitnessScore:
            self.value = values
            self.currFitnessScore = fitnessScore
