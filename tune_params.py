from ecnet import Server
from ecabc import ABC

def __main__():
    ABC abc = ABC() #pass shit in yay
    abc.runAbc()
    # whatever else you do here :) 

class ANN:
    def __init__(config, data):
        self.sv = Server(config_filename=config)
        sv.import_data(
            data,
            sort_type='random',
            data_split=[0.7,0.2,0.1]
        )

    def set_hyperparams():
        # decide how to do this based on how you set the server's params

    def run_ann():
        # Trains neural networks using periodic validation, shuffling learn and validate sets between trials
        sv.train_model(
            validate=True,
            shuffle='lv',
            data_split=[0.7, 0.2, 0.1]
        )

        # Select best neural network from each build node (based on test set performance) to predict for the node
        sv.select_best(dset='test')

        # Predict values for the test data set
        test_results = sv.use_model(dset='test')	

        # Calculates errors for the test set and returns it
        return sv.calc_error('rmse','r2','mean_abs_error','med_abs_error', dset='test')