from ecnet.server import Server
from random import *
import numpy as np

def runNeuralNet(values):
    '''Run the ECNET server'''
    sv = Server()
    sv.vars['learning_rate'] = values[0]
    sv.vars['valid_mdrmse_stop'] = values[1]
    sv.vars['valid_max_epochs'] = values[2]
    sv.vars['valid_mdrmse_memory'] = values[3]
    sv.vars['mlp_hidden_layers[0][0]'] = values[4]
    sv.vars['mlp_hidden_layers[1][0]'] = values[5]

    sv.create_save_env()
    sv.import_data()
    sv.fit_mlp_model_validation('shuffle_lv')
    sv.select_best()
    test_results = sv.use_mlp_model('test')
    sv.output_results(test_results, 'test_results.csv')
    test_errors = sv.calc_error('rmse', 'r2', 'mean_abs_error', 'med_abs_error', dset='test')
    sv.publish_project()
    return test_errors['rmse'][0]

def generateRandomValues():
    values = []
    values.append(np.random.uniform(0.001, 0.1))
    values.append(np.random.uniform(0.000001, 0.01))
    values.append(randint(1250, 2500))
    values.append(randint(500, 2500))
    values.append(randint(12, 32))
    values.append(randint(12, 32))
    return values

def valueFunction(a, b):
    activationNum = np.random.uniform(-1, 1)
    return abs(a + activationNum * (a - b))
