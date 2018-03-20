'''
Copyright 2018 Hernan Gelaf-Romer
University of Massachusetts Lowell - CS
ECNET Research Team
'''

from Bees import *

'''
Wrapper class for the ECNet neural network tasked with finding the ideal hyper parameters by which to run the network via the artificial
bee colony method that can be found here : https://abc.erciyes.edu.tr/.

Can be modified to work with any neural network, or program which requires optimization that is able to output a quntative fitness score
given a certain set of inputs.

Necessary to have ECNET dependancies installed, and Python 3. You can use pip3 install ecnet. Additionally, must have proper config.yml
file within the class folder hiearchy as well as valid molecular csv files with proper formatting to run. Again, this program can ultimately
be adapted to work however with whatever you would like.

'''

class ABC:

    def __init__(self, endValue):

        
        '''Initialize the program by assigning 50 worker bees, one scout, and one onlooker bee which will then be called upon by the program.
        
        Pass an end value, which is the target fitness score you would like to achieve before the program terminates. 
        
        For more information on the functionality of each individual bee, look at the Bees.py file needed to run this program. 
        
        '''
        
        print("INITIALIZING")
        self.employers = []
        self.bestValues = []                    # Store the values that are currently performing the best
        self.onlooker = Bee('onlooker')
        self.bestFitnessScore = 10000           # Store the current best Fitness Score
        self.fitnessAverage = 0
        self.endValue = endValue
        
        for i in range(50):
            print("Creating bee number:", i + 1)
            self.employers.append(Bee('employer', generateRandomValues()))
            self.employers[i].currFitnessScore = runNeuralNet(self.employers[i].values)
            
     '''
     Assign a new position to the given bee, firstBee and secondBee are represented in the form of index values for the list of all bees 
     inside the employers list. 
     
     Careful not to assign the same bees upon running the function, as it will result in one invalid bee until the bee is updated by the 
     program once again, precautions were taken (while loop).
     
    '''
    def assignNewPositions(self, firstBee):
        secondBee = randint(0, len(self.employers) -1)
        while (secondBee == firstBee):
            secondBee = randint(0, len(self.employers) -1)
        self.onlooker.getPosition(self.employers, firstBee, secondBee)

    def getFitnessAverage(self):
        self.fitnessAverage = 0
        self.iterBestFitnessScore = 100000
        for employer in self.employers:
            self.fitnessAverage += employer.currFitnessScore

            if employer.currFitnessScore < self.bestFitnessScore:
                self.bestFitnessScore = employer.currFitnessScore
                self.bestValues = employer.values
                
            if employer.currFitnessScore < self.iterBestFitnessScore:
                self.iterBestFitnessScore = employer.currFitnessScore
                self.iterBestValues = employer.values
                
        self.fitnessAverage /= len(self.employers)

    '''
    Check if the new posotions are better than the average fitness scores, if not assig a new random position to the employer bee 
    and calculate it's fitness score. 
    
    Fitness scores are calculated by running the neural network and obtaining the RMSE that are the result of the given inputs, which is
    the current location the bee is at.
       
    '''
    def checkNewPositions(self, bee):
        if bee.currFitnessScore  > self.fitnessAverage:
            print("Assigning new position for a bee")
            bee.values = self.onlooker.findRandomLocation()
            bee.currFitnessScore = runNeuralNet(bee.values)

    '''
    Check if any current fitness scores are below the end value. If so exit the program, and log all the bee positions which are below
    the end value.
    
    If there is more than one bee with a fitness score of a current location below the end value, then log them all.
    
    ''' 
    def checkIfDone(self):
        keepGoing = True
        for employer in self.employers:
            if employer.currFitnessScore <= self.endValue:
                print("Fitness score =", employer.currFitnessScore)
                print("Values =", employer.values)
                keepGoing = False
        return keepGoing

    '''
    Run the artificial bee colony, generally this is the only method that you will need to use, as the other methods are called here.
    
    A good example of how to run this program properly are as follows :
    
    abc = ABC(6.5)      # Assign the end value to be 6.5, program will terminate only when the end value is reached
    abc.runABC()        # Run the artificial bee colony
    
    '''
    def runABC(self):
        running = True

        while True:
            print("Assigning new positions")
            for i in range(len(self.employers)):
                self.assignNewPositions(i)
            print("Checking if done")
            running = self.checkIfDone()
            if running == False:
                break
            print("Getting fitness average")
            self.getFitnessAverage()
            print("Current fitness average:", self.fitnessAverage)
            print("Checking new positions, assigning random positions to bad ones")
            for employer in self.employers:
                self.checkNewPositions(employer)

            print("Best score:", self.bestFitnessScore)
            print("Best value:", self.bestValues)
            print("Iteration score:", self.iterBestFitnessScore)
            print("Iteratiion values:", self.iterBestValues)
