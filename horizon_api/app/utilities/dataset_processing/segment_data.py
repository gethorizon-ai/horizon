"""Defines helper methods to segment evaluation dataset (e.g., between train and test datasets)."""

import pandas as pd
import scipy


def segment_evaluation_dataset(
    num_unique_data: int, num_test_data_input: int = None
) -> dict:
    """Segment evaluation data into training and test data.
    TODO: update docstring.

    Args:
        num_test_data (int, optional): how many test data points to use. Used if it does not exceed the algorithm's normal
            assignment of test data points. Defaults to None.

    Raises:
        AssertionError: task_request must have evaluation dataset.

    Returns:
        dict: number of training and test data points, along with segmented training and test datasets.
    """
    # Determine ideal sample size based on https://www.calculator.net/sample-size-calculator.html
    confidence_interval = 0.95
    z_score = scipy.stats.norm.ppf((1 + confidence_interval) / 2)
    margin_of_error = 0.1
    population_size = num_unique_data
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

    # Determine size of train dataset such that there is at least 5 and no more than the ideal sample size
    # In between that range, select 20% of the dataset or however much is left after allocating ideal_sample_size to test dataset
    num_train_data = min(
        max(
            5,
            0.2 * num_unique_data,
            num_unique_data - ideal_sample_size,
        ),
        ideal_sample_size,
    )

    # Determine size of test dataset. Allocate at most ideal_sample_size or what's left after allocating num_train_data
    num_test_data = min(ideal_sample_size, num_unique_data - num_train_data)

    # Use num_test_data input value if provided
    if num_test_data_input is not None:
        num_test_data = min(num_test_data_input, num_test_data)

    # Return outputs
    return {
        "num_train_data": num_train_data,
        "num_test_data": num_test_data,
        "train_data_id_list": range(num_train_data),
        "test_data_id_list": range(num_train_data, num_test_data),
    }
