from Bee import *

class ABC:

    def __init__(self, endValue):

        self.scouts = []
        self.employers = []
        self.bestValues = []
        self.cycle = 0
        self.onlooker = Bee('onlooker')
        self.bestFitnessScore = 10000
        self.fitnessAverage = 0
        self.endValue = endValue

        for i in range(10):
            self.scouts.append(Bee('scout'))
            
        for i in range(50):
            self.employers.append(Bee('employer',generateRandomValues()))
            self.employers[i].getFitnessScore(self.employer[i].values)

    def assignNewPositions(self, firstBee):
        secondBee = randint(0, len(self.employers))
        firstCheck = True
        secondCheck = True

        while (secondBee = firstBee):
            secondBee = randint(0, len(beeList))

        self.employer[firstBee].getFitnessScore(onlooker.getPosition(self.employers, firstBee, secondBee))

    def getFitnessAverage(self):
        self.fitnessAverage = 0
        for employer in self.employers:
            self.fitnessAverage += employer.currFitnessScore
        self.fitnessAverage / len(self.employers)
        
    def checkNewPositions(self, bee):
        if bee.currFitnessScore / self.fitnessAverage < 1:
            bee.values = self.onlooker.generateRandomValues()
            bee.currFitnessScore = runNueralNetwork(bee.values)

    def checkIfDone(self):
        keepGoing = True
        for employer in self.employers:
            if employer.currFitnessScore <= endValue:
                print("Fitness score =", employer.currFitnessScore)
                print("Values =", employer.values)
                keepGoing = False
        return keepGoing
            
    def runABC(self):
        running = True

        while True:
            for i in range(self.employers):
                self.assignNewPositions(i)
            running = self.checkIfDone()
            if !running:
                break
            
            self.getFitnessAverage()
            for employer in self.employers:
                self.checkNewPositions(employer)
            

def checkNewScore(beeList, bee):
    greaterThanAverage = True
    summationScore = 0

    for bee in beeList:
        summationScore += bee.currFitnessScore  

    if (bee.currFitnessScore / summationScore) < 1 / (len(beeList) - 1):
        greaterThanAverage = False
        beeList[bee].values = generateRandomValues()
        beeList[bee].currFitnessScore = runNeuralNet(beeList[bee].values)

    return greaterThanAverage
            

            
        
            
