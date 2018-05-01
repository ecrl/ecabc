#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  abc/abc.py
#  v.1.0.0.dev1
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program implements an artificial bee colony to tune ecnet hyperparameters
#

# 3rd party packages (open src.)
from random import randint
import numpy as np
import sys as sys
from pathlib import Path

# artificial bee colony program imports
import abc.bees

### Artificial bee colony object, which contains multiple bee objects ###
class ABC:

    def __init__(self, valueRanges, fitnessFunction=None, endValue = None, iterationAmount = None, amountOfEmployers = 50, filename = 'scores.txt'):
        if endValue == None and iterationAmount == None:
            raise ValueError("must select either an iterationAmount or and endValue")
        if fitnessFunction == None:
            raise ValueError("must pass a fitness function")
        print("***INITIALIZING***")
        self.filename = filename
        self.iterationCount = 0
        self.valueRanges = valueRanges
        self.fitnessFunction = fitnessFunction
        self.employers = []
        self.bestValues = []                    # Store the values that are currently performing the best
        self.onlooker = Bee('onlooker')
        self.bestFitnessScore = None           # Store the current best Fitness Score
        self.fitnessAverage = 0
        self.endValue = endValue
        self.iterationAmount = iterationAmount
        # Initialize employer bees, assign them values/fitness scores
        for i in range(amountOfEmployers):
            sys.stdout.flush()
            sys.stdout.write("Creating bee number: %d \r" % (i + 1))
            self.employers.append(Bee('employer', generateRandomValues(self.valueRanges)))
            self.employers[i].currFitnessScore = self.fitnessFunction(self.employers[i].values)
        print("***DONE INITIALIZING***")
     
    ### Assign a new position to the given bee
    def assignNewPositions(self, firstBee):
        valueTypes = [t[0] for t in self.valueRanges]
        secondBee = randint(0, len(self.employers) -1)
        # Avoid both bees being the same
        while (secondBee == firstBee):
            secondBee = randint(0, len(self.employers) -1)
        self.onlooker.getPosition(self.employers, firstBee, secondBee, self.fitnessFunction, valueTypes)
    
    ### Collect the average fitness score across all employers
    def getFitnessAverage(self):
        self.fitnessAverage = 0
        for employer in self.employers:
            self.fitnessAverage += employer.currFitnessScore
            # While iterating through employers, look for the best fitness score/value pairing
            if self.bestFitnessScore == None or employer.currFitnessScore < self.bestFitnessScore:
                self.bestFitnessScore = employer.currFitnessScore
                self.bestValues = employer.values      
        self.fitnessAverage /= len(self.employers)
    
    ### Check if new position is better than current position held by a bee
    def checkNewPositions(self, bee):
        # Update the bee's fitness/value pair if the new location is better
        if bee.currFitnessScore  > self.fitnessAverage:
            bee.values = generateRandomValues(self.valueRanges)
            bee.currFitnessScore = self.fitnessFunction(bee.values)

    ### If termination depends on a target value, check to see if it has been reached
    def checkIfDone(self, count):
        keepGoing = True
        if self.endValue != None:
            for employer in self.employers:
                if employer.currFitnessScore <= self.endValue:
                    print("Fitness score =", employer.currFitnessScore)
                    print("Values =", employer.values)
                    keepGoing = False
        elif count >= self.iterationAmount:
            keepGoing = False
        return keepGoing
    
    ### Run the artificial bee colony
    def runABC(self):
        running = True
        count = 0

        while True:
            print("Assigning new positions")
            for i in range(len(self.employers)):
                sys.stdout.flush()
                sys.stdout.write('At bee number: %d \r' % (i+1))
                self.assignNewPositions(i)
            print("Getting fitness average")
            self.getFitnessAverage()
            print("Checking if done")
            count+=1
            running = self.checkIfDone(count)
            if running == False and self.endValue != None:
                saveScore(self.bestFitnessScore, self.bestValues, self.iterationCount, self.filename)
                break
            print("Current fitness average:", self.fitnessAverage)
            print("Checking new positions, assigning random positions to bad ones")
            for employer in self.employers:
                self.checkNewPositions(employer)
            print("Best score:", self.bestFitnessScore)
            print("Best value:", self.bestValues)
            if self.iterationAmount != None:
                print("Iteration {} / {}".format(count, self.iterationAmount))
            if running == False:
                saveScore(self.bestFitnessScore, self.bestValues, self.iterationCount, self.filename)
                break
            saveScore(self.bestFitnessScore, self.bestValues, self.iterationCount, self.filename)
            self.iterationCount+=1

        return self.bestValues

