[![UML Energy & Combustion Research Laboratory](http://faculty.uml.edu/Hunter_Mack/uploads/9/7/1/3/97138798/1481826668_2.png)](http://faculty.uml.edu/Hunter_Mack/)

# ECabc : Feature tuning program 

[![PyPI version](https://badge.fury.io/py/ECabc.svg)](https://badge.fury.io/py/ECabc)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/hgromer/Artificial-Bee-Colony/blob/master/LICENSE)

**ECabc** is a generic, small scale feature tuning program that works with any **fitness function**, and **value set**. An **employer bee** is an object which stores a set of values, and a fitness score that correlates to that value, which are both passed by the user. The **onlooker bee** will create a new set of random values, which will then be assigned to a poorly performing employer bee as a replacement. 

The fitness function that is passed must take a tuple of **(value_type, (value_min, value_max)**, with the value types allowed either being a type **float** or a type **int**. The value_type should be passed in as a string. The user may define whether they would like the fitness cost to be minimized or maximized.

# Use

The artificial bee colony can take a mulitude of parameters.
- **endValue**: The target fitness score you would like your values to produce in order to terminate program
- **iterationAmount**: The amount of iterations you would like the program to undergo before terminating
- **amountOfEmployer**: The amount of employer bees the artificial colony will contain, each containing its own set of value and fitness scores correlating to the values.
- **specifyMinOrMax**: Specify whether the fitness cost will be minimized or maximized. Defaults to minimized.
- **setResetIteration**: Specify how many iterations can go by before all employer bees will reset, this may help reduce stagnation a bit. If not specified, bees will never reset.


