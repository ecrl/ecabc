'''
Simple sample script to demonstrate how to use the artificial bee colony
'''

from ABC import *

def fitnessTest(values):  # Fitness function that will be passed to the abc
    fit = 0
    for val in values:
        fit+=val
    return fit
  
values = [('int', (0,100)), ('float', (0,100)), ('int',(0,100))]  # Value type/ranges that will be passed to the abc

abc = ABC(fitnessFunction=fitnessTest, 
          valueRanges=values, 
          amountOfEmployers=10, # Defaults to 50
          iterationAmount=10 # or endValue = 2
         )
abc.runABC()
