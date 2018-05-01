### Private functions to be called by ABC

### Generate a random set of values given a value range
def generateRandomValues(value_ranges):
    values = []
    if value_ranges == None:
        raise RuntimeError("must set the type/range of possible values")
    else:
        # t[0] contains the type of the value, t[1] contains a tuple (min_value, max_value)
        for t in value_ranges:  
            if t[0] == 'int':
                values.append(randint(t[1][0], t[1][1]))
            elif t[0] == 'float':
                values.append(np.random.uniform(t[1][0], t[1][1]))
            else:
                raise RuntimeError("value type must be either an 'int' or a 'float'")
    return values

### Method of generating a value in between the values given
def valueFunction(a, b):  
    activationNum = np.random.uniform(-1, 1)
    return a + abs(activationNum * (a - b))

### Function for saving the scores of each iteration onto a file
def saveScore(score, values, iterationCount, filename):
    # Check to see if the file name already exists on the first iteration
    if (iterationCount == 0 and Path(filename).is_file()):
        print('File:', filename, 'already exists, press y to overwrite')
        if (input() != 'y'):
            print('aborting')
            sys.exit(1)
        else:
            f = open(filename, 'w')
    else:
        f = open(filename, 'a')
    # Add scores to the file
    string = "Score: {} Values: {}".format(score, values)
    f.write(string)
    f.write('\n')
    f.close()
