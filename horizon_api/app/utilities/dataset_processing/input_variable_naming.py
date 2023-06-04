"""Defines helper functions to process input variable names."""

from typing import List


def get_input_variables(dataset_fields: List[str]) -> List[str]:
    """Get input variables from evaluation dataset columns / fields.

    Assumes evaluation dataset has been checked and processed appropriately.

    Args:
        evaluation_dataset (pd.DataFrame): checked and processed evaluation dataset.

    Returns:
        List[str]: list of input variable names.
    """
    input_variables = [
        input_var
        for input_var in dataset_fields
        if input_var not in ["evaluation_data_id", "ground_truth"]
    ]
    return input_variables


def process_input_variables(original_input_variables: List[str]) -> List[str]:
    """Processes input variables by prepending "var_" (to prevent collions with internal variable names).

    Args:
        original_input_variables (List[str]): original input variables.

    Returns:
        List[str]: processed input variables.
    """
    processed_input_variables = [f"var_{var}" for var in original_input_variables]
    return processed_input_variables


def process_input_values(original_input_values: dict) -> dict:
    processed_input_values = {}
    for variable, value in original_input_values.items():
        processed_input_variable = process_input_variables(
            original_input_variables=[variable]
        )
        processed_input_values[processed_input_variable[0]] = value
    return processed_input_values


def normalize_input_variable_list(processed_input_variables: List[str]) -> List[str]:
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
    for var in processed_input_variables:
        if var[0:4] != "var_":
            raise ValueError(
                "Not using processed version of input variables with standard phrase prepended to them."
            )
        normalized_input_variables.append(var[4:])

    return normalized_input_variables
