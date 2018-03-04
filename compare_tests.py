from ecnet.server import Server


def get_scores(iter_amount):
    test_result_generic = 0
    test_result_modified = 0

    for i in range(iter_amount):
        print("Running Iteration:", i + 1)
        test_result_generic += run_server_generic()
        test_result_modified += run_server_modified()

    test_result_generic /= iter_amount
    test_result_modified /= iter_amount

    print("Generic Score:", test_result_generic)
    print("Modified Score:", test_result_modified)


def run_server_generic():
    # Create server object
    sv = Server()
    sv.vars['learning_rate'] = 0.1
    sv.vars['valid_mdrmse_stop'] = 0.01
    sv.vars['valid_max_epochs'] = 1500
    sv.vars['valid_mdrmse_memory'] = 1000
    sv.vars['mlp_hidden_layers[0][0]'] = 5
    sv.vars['mlp_hidden_layers[1][0]'] = 5

    # Create a folder structure for your project
    sv.create_save_env()

    # Import data from file specified in config
    sv.import_data()

    # Fits model(s), shuffling learn and validate sets between trials
    sv.fit_mlp_model_validation('shuffle_lv')

    # Select best trial from each build node to predict for the node
    sv.select_best()

    # Predict values for the test data set
    test_results = sv.use_mlp_model('test')

    # Output results to specified file
    sv.output_results(results=test_results, filename='test_results.csv', dset='test')

    # Calculates errors for the test set
    test_errors = sv.calc_error('rmse', 'r2', 'mean_abs_error', 'med_abs_error', dset='test')

    return test_errors['rmse'][0]

def run_server_modified():
    # Create server object
    sv = Server()
    sv.vars['learning_rate'] = 0.05680061373363629
    sv.vars['valid_mdrmse_stop'] = 0.004675502518033527
    sv.vars['valid_max_epochs'] = 1962
    sv.vars['valid_mdrmse_memory'] = 2364
    sv.vars['mlp_hidden_layers[0][0]'] = 22
    sv.vars['mlp_hidden_layers[1][0]'] = 32


    # Create a folder structure for your project
    sv.create_save_env()

    # Import data from file specified in config
    sv.import_data()

    # Fits model(s), shuffling learn and validate sets between trials
    sv.fit_mlp_model_validation('shuffle_lv')

    # Select best trial from each build node to predict for the node
    sv.select_best()

    # Predict values for the test data set
    test_results = sv.use_mlp_model('test')

    # Output results to specified file
    sv.output_results(results=test_results, filename='test_results.csv', dset='test')

    # Calculates errors for the test set
    test_errors = sv.calc_error('rmse', 'r2', 'mean_abs_error', 'med_abs_error', dset='test')

    return test_errors['rmse'][0]


if __name__ == "__main__":

    get_scores(5)
