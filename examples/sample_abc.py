'''
Simple sample script to demonstrate how to use the artificial bee colony
'''

from ecabc import ABC

def fitnessTest(values):  # Fitness function that will be passed to the abc
    fit = 0
    for val in values:
        fit+=val
    return fit
  
values = [('float', (0,100)), ('float', (0,100)), ('float',(0,100)), ('float', (0, 10000))]  # Value type/ranges that will be passed to the abc
abc = ABC(fitnessFunction=fitnessTest, 
          valueRanges=values, 
          amountOfEmployers=50, # Defaults to 50
          endValue=50
         )
abc.specifyMinOrMax('min')  # Specify that you are looking to maximize the fitness cost -- Defaults to 'min'
abc.runABC()
