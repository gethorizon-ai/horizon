"""Defines helper functions to process input variable names."""

import pandas as pd
from typing import List


def get_input_variables(evaluation_dataset: pd.DataFrame) -> List[str]:
    """Get input variables from evaluation dataset.

    Assumes evaluation dataset has been checked and processed appropriately.

    Args:
        evaluation_dataset (pd.DataFrame): checked and processed evaluation dataset.

    Returns:
        List[str]: list of input variable names.
    """
    input_variables = [
        input_var
        for input_var in evaluation_dataset.columns.to_list()
        if input_var not in ["evaluation_data_id", "ground_truth"]
    ]
    return input_variables


def get_normalized_input_variables(evaluation_dataset: pd.DataFrame) -> List[str]:
    """Get input variables from evaluation dataset without "var_" prepended to them.

    Assumes evaluation dataset has been checked and processed appropriately.

    Args:
        evaluation_dataset (pd.DataFrame): checked and processed evaluation dataset.

    Raises:
        ValueError: checks that evaluation dataset has processed version of input variables with standard phrase prepended to them.

    Returns:
        List[str]: list of input variable names.
    """
    processed_input_variables = get_input_variables(
        evaluation_dataset=evaluation_dataset
    )

    # Check that input variables have been processed with standard phrase prepended to them
    normalized_input_variables = []
    for input_var in processed_input_variables:
        if input_var[0:4] != "var_":
            raise ValueError(
                "Not using processed version of input variables with standard phrase prepended to them."
            )
        normalized_input_variables.append(input_var[4:])

    return normalized_input_variables


def normalize_input_variable_list(input_variable_list: List[str]) -> List[str]:
    """Normalize list of processed input variables by removing "var_" prepending from them.

    Assumes input variables have been processed appropriately.

    Args:
        input_variable_list (List[str]): processed list of input variables.

    Raises:
        ValueError: checks for processed version of input variables with standard phrase prepended to them.

    Returns:
        List[str]: list of normalized input variable names.
    """
    # Check that input variables have been processed with standard phrase prepended to them
    normalized_input_variables = []
    for input_var in input_variable_list:
        if input_var[0:4] != "var_":
            raise ValueError(
                "Not using processed version of input variables with standard phrase prepended to them."
            )
        normalized_input_variables.append(input_var[4:])

    return normalized_input_variables
