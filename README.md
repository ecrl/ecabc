**NOTE. THIS VERSION OF ECABC IS DEPRECATED. VERSIONS 2.0.0 WILL BRING VARIOUS QUALITY OF LIFE AND ALGORITHM CHANGES THAT WILL IMPROVE THE EASE OF USE AND EFFICIENCY OF THIS SOFTWARE. VERSIONS 2.0.0 CAN BE TRACKED IN THE 2.0.0 BRANCH.**


[![UML Energy & Combustion Research Laboratory](http://faculty.uml.edu/Hunter_Mack/uploads/9/7/1/3/97138798/1481826668_2.png)](http://faculty.uml.edu/Hunter_Mack/)

# ECabc : Feature tuning program 

[![GitHub version](https://badge.fury.io/gh/hgromer%2Fecabc.svg)](https://badge.fury.io/gh/hgromer%2Fecabc)
[![PyPI version](https://badge.fury.io/py/ECabc.svg)](https://badge.fury.io/py/ECabc)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/hgromer/Artificial-Bee-Colony/blob/master/LICENSE)

**ECabc** is a generic, small scale feature tuning program that works with any **fitness function**, and **value set**. An **employer bee** is an object which stores a set of values, and a fitness score that correlates to that value, which are both passed by the user. The **onlooker bee** will create a new set of random values, which will then be assigned to a poorly performing employer bee as a replacement. 

The fitness function that is passed must take a tuple of **(value_type, (value_min, value_max))**, with the value types allowed either being a type **float** or a type **int**. The value_type should be passed in as a string. The user may define whether they would like the fitness cost to be minimized or maximized. The user may also decide whether they would like visual feeback by turning print statements either one or off.

All scores will be saved in a file that you can specify in the constructor argument. The file name will default to **scores.txt** and will hold the information of each iterations best fitness score and values.

# Installation

### Prerequisites:
- Have python 3.5 installed
- Have the ability to install python packages

### Method 1: pip
If you are working in a Linux/Mac environment
- **sudo pip install ecabc**

Alternatively, in a windows environment, make sure you are running cmd as administrator
- **pip install ecabc**

Note: if multiple Python releases are installed on your system (e.g. 2.7 and 3.5), you may need to execute the correct version of pip. For Python 3.5, change **"pip install ecabc"** to **"pip3 install ecabc"**.

### Method 2: From source
- Download the ECabc repository, navigate to the download location on the command line/terminal, and execute 
**"python setup.py install"**. 

Additional package dependencies (Numpy) will be installed during the ECabc installation process.

To update your version of ECabc to the latest release version, use "**pip install --upgrade ecabc**

# Installation

### Prerequisites:
- Have python 3.5 installed
- Have the ability to install python packages

### Method 1: pip
If you are working in a Linux/Mac environment
- **sudo pip install ecabc**

Alternatively, in a windows environment, make sure you are running cmd as administrator
- **pip install ecabc**

Note: if multiple Python releases are installed on your system (e.g. 2.7 and 3.5), you may need to execute the correct version of pip. For Python 3.5, change **"pip install ecabc"** to **"pip3 install ecabc"**.

### Method 2: From source
- Download the ECabc repository, navigate to the download location on the command line/terminal, and execute 
**"python setup.py install"**. 

Additional package dependencies (Numpy) will be installed during the ECabc installation process.

To update your version of ECabc to the latest release version, use "**pip install --upgrade ecabc**".

# Usage

The artificial bee colony can take a mulitude of parameters.
- **endValue**: The target fitness score you would like your values to produce in order to terminate program
- **iterationAmount**: The amount of iterations you would like the program to undergo before terminating
- **amountOfEmployer**: The amount of employer bees the artificial colony will contain, each containing its own set of value and fitness scores correlating to the values.
- **specifyMinOrMax**: Specify whether the fitness cost will be minimized or maximized. Defaults to minimized.
- **printInfo**: Accepts a boolean value, if set to False will prevent any print statements from occuring, this will increase the speed of your program if your fitness function isn't computationally expensive.

# Example

```python
from ecabc.abc import ABC

def fitnessTest(values):  # Fitness function that will be passed to the abc
    fit = 0
    for val in values:
        fit+=val
    return fit
  
values = [('float', (0,100)), ('float', (0,100)), ('float',(0,100)), ('float', (0, 10000))]  # Value type/ranges that will be passed to the abc
abc = ABC(fitnessFunction=fitnessTest, 
          valueRanges=values, 
          amountOfEmployers=50, # Defaults to 50
          endValue=50           # Or iterationAmount
         )
         
abc.runABC() # Run the artificial bee colony
```


