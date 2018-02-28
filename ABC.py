from Bee import *

class ABC:

    def __init__(self):

        self.scouts = []
        self.employers = []
        self.bestValues = []
        self.cycle = 0
        self.onlooker = Bee('onlooker')
        self.bestFitnessScore = 10000

        for i in range(10):
            self.scouts.append(Bee('scout'))
            
        for i in range(50):
            self.employers.append(Bee('employer',generateRandomValues()))
            self.employers[i].getFitnessScore(self.employer[i].values)

    def runIteration:
        fistBee = randint(0, len(self.employers))
        secondBee = randint(0, len(self.employers))

        while (secondBee = firstBee):
            secondBee = randint(0, len(beeList))

        while self.cycle < 5:
            self.employer[firstBee].getFitnessScore(onlooker.getPosition(self.employers, firstBee, secondBee))


def checkNewScore(beeList, bee):
    averageScore = 0

    for bee in beeList:
        averageScore += bee.currFitnessScore

    if (bee.currFitnessScore / averageScore) < 1 / (len(beeList) - 1):
        beeList[bee].values = generateRandomValues()
        beeList[bee].currFitnessScore = runNeuralNet(beeList[bee].values)

            

            
        
            
