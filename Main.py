import random
import copy

NP=100 # total population
foodNumber=NP/2 # half the population of bees = number of food sources
globalMin=1000000 # the lowest error
globalParams=[1,2,3]    # the parameters of the global min
limit=100 # the max no. of times an employer bee can be tried to improved, after this it turns into a scout
maxCycle=3000 #total number of cycles the code can run

upperLimits = [6,7,8]
lowerLimits = [1,2,3]
#dimensions = [A,B,C] #dimensions of the search space

class Bee:
    def __init__(self):
        self.position = []
        self.currValue = None
        self.fitnessScore = None
        for i in range(len(upperLimits)):
            self.position.append(lowerLimits[i]+random.random(0,1)*(upperLimits[j]-lowerLimits[j]))

#error is the error returned from runnning the ann    
    def calculateFitness(self, error):
        if error >= 0:
            self.fitness = 1/(error+1)
        else:
            self.fitness = 1 + abs(error)

class employedBee(Bee):
    def __init__(self):
		self.probability = 0
		self.count = 0

    # any methods that are only for employed bees?
    def moveEmployerBee (self, Bee2):
        j = random.randint(0,len(upperLimits))
        mutant = copy.deepcopy(self)
        mutant.position[j] = self.position[j]+random.random(-1,1)*(self.position[j]-Bee2.position[j])
        error = mutant.runANN #MAKE THIS A THING
        mutant.calculateFitness(error)
        if mutant.fitness>self.fitness:
            for j in range(len(upperLimits)):
                self.position[j] = mutant.position[j]
            self.fitnessScore = mutant.fitnessScore
            self.currValue = mutant.currValue
            self.counter = 0
        else:
            self.counter += 1

class onlookerBee(Bee):
    #def __init__(self):
        # you should look up how to call the superclass constructor in python idk how to do it
    def moveOnlookerBee (self, Bee2, chosenEmployerBee):
        j = random.randint(0,len(upperLimits))
        #make mutant
        mutant = copy.deepcopy(self)
        mutant.position[j] = self.position[j]+random.random(-1,1)*(self.position[j]-Bee2.position[j])
        error = mutant.runANN #MAKE THIS A THING
        mutant.calculateFitness(error)
        if mutant.fitness>self.fitness:
            for j in range(len(upperLimits)):
                chosenEmployerBee.position[j] = mutant.position[j]
            chosenEmployerBee.fitnessScore = mutant.fitnessScore
            chosenEmployerBee.currValue = mutant.currValue
            
            #onlooker bee turns into employer?? CHECK
        #else:

class ABC:
    def __init__(self, maxCycle, foodNumber, ANN):
        self.bestFitness = None
        self.bestPosition = None
        self.employedList = [employedBee() for i in range (foodNumber)]
        self.onlookerList = [onlookerBee() for i in range (foodNumber)]
        self.cycleNumber = None
        self.maxCycle = maxCycle
        #ANN is placeholder for how am I going to pass in the problem the abc is solving
        self.foodNumber = foodNumber
    def runABC(self):
        while (self.cycleNumber < self.maxCycle):
            for i in range(foodNumber):
                k = i
                while k == i:
                    k = random.randint(0,foodNumber)
                self.employedList[i].moveEmployerBee(employedList[k])
                totalFit += self.employedList[i].fitness
            for i in range(foodNumber):  
                self.employedList[i].probability = self.employedList[i].fitness/totalFit
            #pick based on probability 
            for i in range(foodNumber):
                x = random.uniform(0,1)
                totalProbability = 0.0
                for item, item_probability in zip (employedList,employedList.probability):
                    totalProbability += item_probability
                    if x < totalProbability: 
                        chosenEmployerBee= item
                        break
                onlookerList[i] = chosenEmployerBee    
                k = i
                while k == i:
                    k = random.randint(0,foodNumber)
                self.onlookerList[i].moveOnlookerBee(employedList[k], chosenEmployerBee)
            #scout bee phase
            for i in range(foodNumber):
                if employedList[i].counter > 100:
                    employedList[i] = employerBee() #####CHECK THIS IS RIGHT

            #memorize best solution
            for i in range(foodNumber):
                if globalMin < self.employedList[i].currValue:
                    globalMin = self.employedList[i].currValue 
                    for j in range(upperLimits):
                        globalParams[j] = self.employedList[i].position[j]

            self.cycleNumber += 1

