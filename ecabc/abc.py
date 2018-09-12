#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.1.2.0
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program implements an artificial bee colony to tune ecnet hyperparameters
#

# 3rd party packages (open src.)
import sys as sys
from random import randint
import numpy as np
from multiprocessing import Pool

# artificial bee colony packages
from ecabc.bees import Bee
from ecabc.settings import Settings
from ecabc.output import Output

### Artificial bee colony object, which contains multiple bee objects ###
class ABC:

    def __init__(self, valueRanges, fitnessFunction=None, endValue=None, iterationAmount=None,\
     amountOfEmployers=50, filename='settings.json', printInfo=True, importing=False, processes=5):
        if endValue == None and iterationAmount == None:
            raise ValueError("must select either an iterationAmount or and endValue")
        if fitnessFunction == None:
            raise ValueError("must pass a fitness function")
        self.saving = filename is not None
        self.iterationCount = 0
        self.output = Output(printInfo)
        self.settings = Settings(valueRanges, iterationAmount, endValue, amountOfEmployers, filename, processes)
        if self.saving:
            if importing:
                try:
                    self.settings.importSettings()
                except FileNotFoundError:
                    self.output.print("Creating new settings file")
                self.settings.saveSettings()
            else:
                self.settings.saveSettings()
        if self.settings._processes > 0:
            self.pool = Pool(processes)
        self.fitnessFunction = fitnessFunction
        self.employers = []
        self.onlooker = Bee('onlooker')
        self.fitnessAverage = 0
        # Initialize employer bees, assign them values/fitness scores
        self.output.print("***INITIALIZING ABC***")
        self.createEmployerBees(amountOfEmployers)
        self.output.print("***DONE INITIALIZING***")
     
    ### Assign a new position to the given bee
    def assignNewPositions(self, firstBee):
        valueTypes = [t[0] for t in self.settings._valueRanges]
        secondBee = randint(0, len(self.employers) -1)
        # Avoid both bees being the same
        while (secondBee == firstBee):
            secondBee = randint(0, len(self.onlooker.bestEmployers) -1)
        self.onlooker.getPosition(self.employers, firstBee, secondBee, self.fitnessFunction, valueTypes)
    
    ### Collect the average fitness score across all employers
    def getFitnessAverage(self):
        self.fitnessAverage = 0
        for employer in self.employers:
            self.fitnessAverage += employer.currFitnessScore
            # While iterating through employers, look for the best fitness score/value pairing
            if self.isBetterThanCurrBest(employer):
                self.settings._bestScore = employer.currFitnessScore
                self.settings._bestValues = employer.values  
        self.fitnessAverage /= len(self.employers)

    ### Generate a random set of values given a value range
    def generateRandomValues(self):
        values = []
        if self.settings._valueRanges == None:
            raise RuntimeError("must set the type/range of possible values")
        else:
            # t[0] contains the type of the value, t[1] contains a tuple (min_value, max_value)
            for t in self.settings._valueRanges:  
                if t[0] == 'int':
                    values.append(randint(t[1][0], t[1][1]))
                elif t[0] == 'float':
                    values.append(np.random.uniform(t[1][0], t[1][1]))
                else:
                    raise RuntimeError("value type must be either an 'int' or a 'float'")
        return values
    
    ### Check if new position is better than current position held by a bee
    def checkNewPositions(self):
        # If multi processing
        if self.settings._processes > 0:
            modified_bees = []
            for bee in self.employers:
                if self.isWorseThanAverage(bee):
                    bee.values = self.generateRandomValues()
                    bee.currFitnessScore = self.pool.apply_async(self.fitnessFunction, [bee.values])
                    modified_bees.append(bee)
                else:
                    # Assign the well performing bees to the onlooker
                    self.onlooker.bestEmployers.append(bee)
            for bee in modified_bees:
                bee.currFitnessScore = bee.currFitnessScore.get()
                self.settings.update(bee.currFitnessScore, bee.values)

        # No multiprocessing
        else:
            for bee in self.employers:
                if self.isWorseThanAverage(bee):
                    bee.values = self.generateRandomValues()
                    bee.currFitnessScore = self.fitnessFunction(bee.values)

    ### If termination depends on a target value, check to see if it has been reached
    def checkIfDone(self, count):
        stop = False
        if self.settings._endValue != None:
            if self.betterThanEndValue(self.settings._bestScore):
                stop = True
        elif count >= self.settings._iterationAmount:
            stop = True
        return stop
    
    ### Create employer bees
    def createEmployerBees(self, amountOfEmployers):
        # If multiprocessing
        if self.settings._processes > 0:
            for i in range(amountOfEmployers):
                self.employers.append(Bee('employer', self.generateRandomValues()))
                self.employers[i].currFitnessScore = self.pool.apply_async(self.fitnessFunction, [self.employers[i].values])
            for i in range(amountOfEmployers):
                self.employers[i].currFitnessScore = self.employers[i].currFitnessScore.get()
                self.output.print("Bee number {} created".format(i+1))

        # No multiprocessing
        else:
            for i in range(amountOfEmployers):
                self.employers.append(Bee('employer', self.generateRandomValues()))
                self.employers[i].currFitnessScore = self.fitnessFunction(self.employers[i].values)
                self.output.print("Bee number {} created".format(i+1))
    
    ### Specify whether the artificial bee colony will maximize or minimize the fitness cost
    def minimize(self, minimize):
        self.settings._minimize = minimize
        
    ### Return whether the bee has a fitness score worse than the average
    def isWorseThanAverage(self, bee):
        return (self.settings._minimize == True and bee.currFitnessScore  > self.fitnessAverage) or\
               (self.settings._minimize == False and bee.currFitnessScore < self.fitnessAverage)
    
    ### Return whether the bee's fitness score hits the specified end value
    def betterThanEndValue(self, score):
        return (self.settings._minimize == True and score <= self.settings._endValue) or\
               (self.settings._minimize == False and score >= self.settings._endValue)

    ### Return whether a bee's fitness average is better than the current best fitness score
    def isBetterThanCurrBest(self, bee):
        return self.settings._bestScore == None or (self.settings._minimize == True and bee.currFitnessScore < self.settings._bestScore) or\
               (self.settings._minimize == False and bee.currFitnessScore > self.settings._bestScore)

    ### Decide whether print statements will occur
    def printInfo(self, yn):
        self.output._print = yn

    ### Run the artificial bee colony
    def runABC(self):

        while True:
            
            self.onlooker.bestEmployers.clear()
            self.output.print("Assigning new positions")
            for i in range(len(self.onlooker.bestEmployers)):
                self.output.print('At bee number: %d \r' % (i+1))
                self.assignNewPositions(i)
            self.output.print("Getting fitness average")
            self.getFitnessAverage()
            self.output.print("Current fitness average: {}".format(self.fitnessAverage))
            if self.settings._iterationAmount != None:
                self.output.print("Iteration {} / {}".format(self.iterationCount+1, self.settings._iterationAmount))
            self.iterationCount+=1
            self.output.print("Checking if done")
            
            if self.saving:
                self.settings.saveSettings()
            if self.checkIfDone(self.iterationCount):
                break

            self.output.print("Checking new positions, assigning random positions to bad ones")
            self.checkNewPositions()
            self.output.print("Best score: {}".format(self.settings._bestScore))
            self.output.print("Best value: {}".format(self.settings._bestValues))

        return self.settings._bestValues
