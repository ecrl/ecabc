'''
Copyright 2018 Hernan Gelaf-Romer
University of Massachusetts Lowell - CS
ECNET Researcher
'''

from Functions import *

'''
Class which contains the individual bees that will be used to run the artifical bee colony programmed in ABC.py. More information on how
that program works can be found within that file.

More information on how an artificial bee colony works can be found here : https://abc.erciyes.edu.tr/.

'''

class Bee:
    
    '''
    Each be must be given a type, which can be Worker/Onlooker/Scout, documentation on the responsibility of each bee can be found below, 
    and also at https://abc.erciyes.edu.tr/.
    
    Each employer bee will store its position, or set of values that can be run through the ECNet neural network in order to obtain the fitness score, 
    or RMSE values of the outputs produced the by the value sets.
    
    Each employer bee also stores its current fitness score.
    
    '''
    def __init__(self, beeType, values=[]):

        self.beeType = beeType
        
        if beeType == "employer":               # Only the employer bees should store values/fitness scores
            self.values = values            
            self.currFitnessScore = 100000

    '''
    Onlooker Bee Functions
    
    The onlooker bee is responsible for comparing the positions of random bees and passing it to the first worker bee, which will then 
    test the new position compared to its old, if the new position is better, it will store the new values, and replace its current fitness
    score.
    
    The valueFunction implementation can be found in functions.py, and is the mathematical standard when it comes to comparing positions
    in regards to artificial bee colonies. 
    
    
    '''

    def getPosition(self, beeList, firstBee, secondBee):
        newValues = []
        currValue = 0

        for i in range(6):
            currValue = valueFunction(beeList[firstBee].values[i], beeList[secondBee].values[i])
            if i > 1:
                currValue = int(currValue)
            if currValue <= 0:
                currValue += 1
            newValues.append(currValue)

        beeList[firstBee].getFitnessScore(newValues)

    '''
    Employer Bee Functions
    
    The employer bee's sole function is to calculate the fitness score of the new position it is passed, and compare it to its current 
    fitness score. If the new fitness score is better, then the old position will be replaced with the new position, as well as the fitness
    scores.
    
    '''

    def getFitnessScore(self, values):
        fitnessScore = runNeuralNet(values)
        if fitnessScore < self.currFitnessScore:
            self.value = values
            self.currFitnessScore = fitnessScore
