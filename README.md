[![UML Energy & Combustion Research Laboratory](http://faculty.uml.edu/Hunter_Mack/uploads/9/7/1/3/97138798/1481826668_2.png)](http://faculty.uml.edu/Hunter_Mack/)

# ECabc : Feature tuning program 

[![GitHub version](https://badge.fury.io/gh/ECRL%2Fecabc.svg)](https://badge.fury.io/gh/ECRL%2Fecabc.svg)
[![PyPI version](https://badge.fury.io/py/ECabc.svg)](https://badge.fury.io/py/ECabc)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ECRL/Artificial-Bee-Colony/blob/master/LICENSE)

**ECabc** is a generic, small scale feature tuning program that works with any **fitness function**, and **value set**. An **employer bee** is an object which stores a set of values, and a fitness score that correlates to that value, which are both passed by the user. The **onlooker bee** will create a new set of random values, which will then be assigned to a poorly performing employer bee as a replacement. 

The fitness function that is passed must take a tuple of **(value_type, (value_min, value_max))**, with the value types allowed either being a type **float** or a type **int**. The value_type should be passed in as a string. The user may define whether they would like the fitness cost to be minimized or maximized. The user may also decide whether they would like visual feeback by turning print statements either one or off.

All scores will be saved in a file that you can specify in the constructor argument. The file name will default to **settings.json** and will hold the information of each iterations best fitness score and values.

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
- **value_ranges**: Your value ranges. Values must be passed as a list of tuples with a **type/(min_value, max_value)** pairing. See the example file for more details.
- **fitness_fxn**: The user defined function that will be used to generate the cost of each employer bee's values.
- **file_logging**: Accepts 'debug', 'info', 'warn', 'error', 'critical' or 'disabled'. This will save a log file under a logs directory. If set to 'disabled', won't output to console. Defaults to 'disabled'.
- **print_level**: Accepts 'debug', 'info', 'warn', 'error', 'critical' or 'disabled'. This will print out log information to the console, and is less costly compared to saving logs to a file. If set to 'disabled', won't output to console. Defaults to 'info'.
- **processes**: Decide how many processes you'd like to have running at a time. A process will run the fitness function once per iteration. Processes run in parallel, and thus the more processes you utilize, the more fitness functions can run concurrently, cutting program run time significantly. If your fitness function takes 5 seconds to execute. Utilizing 50 bees, and 5 processes, calculating the values for all bees will take 50 seconds, rather than 250. Be mindful that this will increase CPU usage heavily, and you should be careful with how many processes you allow a time, to avoid a crash or computer freeze. **If your fitness function is trivial, set processes to 0. Process spawning is expensive, and only worth it for costly fitness functions.** Defaults to 5.

The artificial bee colony also utilizes a variety to methods to toggle certain settings.
- **minimize**: If set to true, the bee colony will minimize the fitness function, otherwise it will maximize it.
- **import_settings**: Accepts a json file by name. If the file exists, the artificial bee colony will import and use these settings, then return True. If the file doesn't exist, an error message will be logged, settings will be set to default, and the function will return False.
- **save_settings**: Accepts a json file name. If the file exists, the artificial bee colony settings will be saved to this file.

# 2.0.0 Update
Update 2.0.0 changed ecabc quite a bit. In order to ensure code mantainability, in addition allowing the users to have more control, we have un-automated the run process in place of 3/4 methods the user must now call to use the abc properly. Employer bees are not automatically created for you anymore. The runABC() method has been removed as well. Below is an example of how to properly use the abc in the easiest way possible.

# Example

```python
'''
Simple sample script to demonstrate how to use the artificial bee colony, this script is a simple example, which is just
used to demonstrate how the program works.

If an ideal day is 70 degrees, with 37.5% humidity. The fitness functions takes four values and tests how 'ideal' they are.
The first two values input will be added to see how hot the day is, and the second two values will be multiplied to see how much
humidity there is. The resulting values will be compared to 70 degrees, and 37.5% humidity to determine how ideal the day those 
values produce is. 

The goal is to have the first two values added up to as close to 70 as possible, while the second two values multiply out to as 
close to 37.5 as possible.
'''

from eabc import *
import os
import time

def idealDayTest(values):  # Fitness function that will be passed to the abc
    temperature = values[0] + values[1]       # Calcuate the day's temperature
    humidity = values[2] * values[3]          # Calculate the day's humidity
    
    cost_temperature = abs(70 - temperature)  # Check how close the daily temperature to 70
    cost_humidity = abs(37.5 - humidity)      # Check how close the humidity is to 37.5

    return cost_temperature + cost_humidity   # This will be the cost of your fitness function generated by the values

         # First value      # Second Value     # Third Value      # Fourth Value
values = [('int', (0,100)), ('int', (0,100)), ('float',(0,100)), ('float', (0, 100))]

start = time.time()
abc = ABC(fitness_fxn=idealDayTest, 
          value_ranges=values, 
          print_level='warn',
          file_level='debug'
         )
abc.create_employers()
while True:
    abc.save_settings('{}/settings.json'.format(os.getcwd()))
    abc.calc_average()
    abc.calc_new_positions()
    abc.check_positions()
    if (abc.get_best_performer()[0] < 2):
        break
print("execution time = {}".format(time.time() - start))
```


