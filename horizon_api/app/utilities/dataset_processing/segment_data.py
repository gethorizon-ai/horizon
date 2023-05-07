"""Defines helper methods to segment evaluation dataset (e.g., between train and test datasets)."""

import pandas as pd
import scipy


def segment_evaluation_dataset(
    evaluation_dataset: pd.DataFrame, num_test_data_input: int = None
) -> dict:
    """Segment evaluation data into training and test data.

    Args:
        num_test_data (int, optional): how many test data points to use. Used if it does not exceed the algorithm's normal
            assignment of test data points. Defaults to None.

    Raises:
        AssertionError: task_request must have evaluation dataset.

    Returns:
        dict: number of training and test data points, along with segmented training and test datasets.
    """
    if not isinstance(evaluation_dataset, pd.DataFrame):
        raise AssertionError(
            "Must add evalution dataset first before computing data lengths in evaluation dataset."
        )

    # Determine ideal sample size based on https://www.calculator.net/sample-size-calculator.html
    confidence_interval = 0.95
    z_score = scipy.stats.norm.ppf((1 + confidence_interval) / 2)
    margin_of_error = 0.1
    population_size = len(evaluation_dataset)
    population_proportion = 0.5
    ideal_sample_size = int(
        (
            (z_score**2)
            * population_proportion
            * (1 - population_proportion)
            / (margin_of_error**2)
        )
        / (
            1
            + (
                (z_score**2)
                * population_proportion
                * (1 - population_proportion)
                / ((margin_of_error**2) * population_size)
            )
        )
    )

    # Determine size of train dataset such that there is at least 5 and at most ideal_sample_size data points. In between that range,
    # allocate at least 20% of the dataset or however much is left after allocating ideal_sample_size to test dataset
    num_train_data = max(
        5,
        min(
            ideal_sample_size,
            max(
                0.2 * len(evaluation_dataset),
                len(evaluation_dataset) - ideal_sample_size,
            ),
        ),
    )

    # Determine size of test dataset. Allocate at most ideal_sample_size or what's left after allocating num_train_data
    num_test_data = min(ideal_sample_size, len(evaluation_dataset) - num_train_data)

    print(f"num_train_data: {num_train_data}")
    print(f"num_test_data: {num_test_data}")

    # # Assume 80/20 split with at least 5 and at most 10 training data points
    # num_train_data = min(10, max(5, int(len(evaluation_dataset) * 0.2)))

    # # Assume at most 15 test data points
    # num_test_data = min(15, len(evaluation_dataset) - num_train_data)

    # Use num_test_data input value if provided
    if num_test_data_input is not None:
        num_test_data = min(num_test_data_input, num_test_data)

    # Assign input and ground truth data. Keep evaluation_data_id column in all.
    input_data_train = (
        evaluation_dataset.iloc[:num_train_data, :]
        .drop("ground_truth", axis=1)
        .reset_index(drop=True)
    )
    ground_truth_data_train = evaluation_dataset.iloc[:num_train_data, :][
        ["evaluation_data_id", "ground_truth"]
    ].reset_index(drop=True)
    input_data_test = (
        evaluation_dataset.iloc[
            num_train_data : num_train_data + num_test_data,
            :,
        ]
        .drop("ground_truth", axis=1)
        .reset_index(drop=True)
    )
    ground_truth_data_test = evaluation_dataset.iloc[
        num_train_data : num_train_data + num_test_data,
        :,
    ][["evaluation_data_id", "ground_truth"]].reset_index(drop=True)

    # Return outputs
    return {
        "num_train_data": num_train_data,
        "num_test_data": num_test_data,
        "input_data_train": input_data_train,
        "ground_truth_data_train": ground_truth_data_train,
        "input_data_test": input_data_test,
        "ground_truth_data_test": ground_truth_data_test,
    }
