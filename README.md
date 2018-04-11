# Artificial-Bee-Colony
Artificial Bee Colony for hyper-parameter selection on ECNET

Ability to model an artificial bee colony by creating scout, onlooker, and employers bees via the Bee.py module. Each bee type will
contain its own set of functions that apply to an real bee colony. ABC.py will utilize the bees and create a colony, which will contain
various different lists of the three bee types and simulate a real bee colony. 

Positions = values for the 6 hyper-parameters of ECNET

Employer bees - Generate fitness scores of 'nectar' at its current position.
Scout bees - Find new locations for 'nectar' source at random.
Onlooker bees - Generate new position for employer bees by getting a position between bee A and a random bee b for all employers in the colony

Additional scripts included to demonstrate how to run the bee colony, and how to compare the test values against the generic ECNET hyperparameter test results.

Dependencies required: 
ecnet/pandas/numpy/random

# Use

The artificial bee colony can take a mulitude of parameters.
__endValue: The target fitness score you would like your values to produce in order to terminate program__
__iterationAmount: The amount of iterations you would like the program to undergo before terminating__
__amountOfEmployer: The amount of employer bees the artificial colony will contain, each containing its own set of value and fitness scores correlating to the values.__

Note:

While the endValue and iterationAmount are both defaulted to None, you must choose one for program termination.
