from ecnet.server import Server

def get_scores(iter_amount):
    test_result_generic = 0
    test_result_modified = 0

    '''for i in range(iter_amount):
        print("Running Iteration:", i + 1)
        test_result_generic += run_server_generic()
        test_result_modified += run_server_modified()

    test_result_generic /= iter_amount
    test_result_modified /= iter_amount'''

    generic_score = run_server_generic()
    modifed_score = run_server_modified()

    print("Generic Scores:", generic_score)
    print("Modified Scores:", modifed_score)


def run_server_generic():
    # Create server object
    sv = Server()
    sv.vars['learning_rate'] = 0.1
    sv.vars['valid_mdrmse_stop'] = 0.01
    sv.vars['valid_max_epochs'] = 1500
    sv.vars['valid_mdrmse_memory'] = 1000

    sv.create_save_env()

    sv.vars['data_split'] = [0.7, 0.3, 0.0]                # for ‘slv’ data, only split data for training (learning + validation)
    sv.import_data('cn_model_v1_slv.csv')                  # import the training data
    sv.fit_mlp_model_validation('shuffle_lv')

    sv.vars['data_split'] = [0.0, 0.0, 1.0]                # 100% of ‘st’ data will be put into the test set
    sv.import_data('cn_model_v1_st.csv')                   # import the static test set data
    sv.select_best('test')
    test_results = sv.use_mlp_model()

    # Output results to specified file
    sv.output_results(results=test_results, filename='test_results_generic_test_master.csv')

    # Calculates errors for the test set
    test_errors = sv.calc_error('rmse', 'r2', 'mean_abs_error', 'med_abs_error', dset = 'test')
    return test_errors

def run_server_modified():
    # Create server object
    sv = Server()
    sv.vars['learning_rate'] = 0.06831226025740823
    sv.vars['valid_mdrmse_stop'] = 0.0013627967309420112
    sv.vars['valid_max_epochs'] = 1815
    sv.vars['valid_mdrmse_memory'] = 1934
    sv.vars['mlp_hidden_layers[0][0]'] = 13
    sv.vars['mlp_hidden_layers[1][0]'] = 12

    sv.create_save_env()

    sv.vars['data_split'] = [0.7, 0.3, 0.0]               # for ‘slv’ data, only split data for training (learning + validation)
    sv.import_data('cn_model_v1_slv.csv')                 # import the training data
    sv.fit_mlp_model_validation('shuffle_lv')

    sv.vars['data_split'] = [0.0, 0.0, 1.0]                # 100% of ‘st’ data will be put into the test set
    sv.import_data('cn_model_v1_st.csv')                   # import the static test set data
    sv.select_best('test')
    test_results = sv.use_mlp_model()

    # Output results to specified file
    sv.output_results(results=test_results, filename='test_results_modified_test_master.csv')

    # Calculates errors for the test set
    test_errors = sv.calc_error('rmse', 'r2', 'mean_abs_error', 'med_abs_error', dset = 'test')

    return test_errors


if __name__ == "__main__":

    get_scores(1)
