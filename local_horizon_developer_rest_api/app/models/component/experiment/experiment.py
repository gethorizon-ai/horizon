import pandas as pd


class Experiment:
    def __init__(self, user_objective, input_variables, evaluation_dataset, input_values_test, ground_truth_test,
                 input_values_train, ground_truth_train):
        self.user_objective = user_objective
        self.input_variables = input_variables
        self.input_values_test = input_values_test
        self.ground_truth_test = ground_truth_test
        self.input_values_train = input_values_train
        self.ground_truth_train = ground_truth_train
        self.evaluation_dataset = evaluation_dataset

    @classmethod
    def from_dict(cls, experiment_dict):
        # Convert data from dicts to pandas DataFrames
        experiment_dict['input_values_test'] = pd.DataFrame(
            experiment_dict['input_values_test'])
        experiment_dict['ground_truth_test'] = pd.DataFrame(
            experiment_dict['ground_truth_test'])
        experiment_dict['input_values_train'] = pd.DataFrame(
            experiment_dict['input_values_train'])
        experiment_dict['ground_truth_train'] = pd.DataFrame(
            experiment_dict['ground_truth_train'])
        experiment_dict['evaluation_dataset'] = pd.DataFrame(
            experiment_dict['evaluation_dataset'])

        return cls(**experiment_dict)
