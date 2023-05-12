"""Contains helper functions to process and extract info from evaluation dataset."""

from . import data_length
from . import llm_applicability
import os
import csv
import re
import pandas as pd


def check_evaluation_dataset_and_data_length(
    dataset_file_path: str, synthetic_data_generation: bool = False
) -> None:
    """Checks contents of evaluation dataset for potential errors and if data lengths meet llm token limits.

    Args:
        dataset_file_path (str): file path to evaluation dataset.
        synthetic_data_generation (bool, optional): whether this task request is to generate synthetic data. Defaults to False.

    Raises:
        AssertionError: checks if input and output data lengths exceed token limits of available llms.
        AssertionError: checks if input and output data lengths exceed token limits of available llms.
    """
    # Check contents of evaluation dataset for potential errors
    check_evaluation_dataset(
        dataset_file_path=dataset_file_path,
        synthetic_data_generation=synthetic_data_generation,
    )

    # Get evaluation dataset
    evaluation_dataset = get_evaluation_dataset(
        dataset_file_path=dataset_file_path, escape_curly_braces=True
    )

    # Check that evaluation data lengths are appropriate
    evaluation_data_length = data_length.get_evaluation_data_length(
        evaluation_dataset=evaluation_dataset, unescape_curly_braces=True
    )
    max_input_tokens = evaluation_data_length["max_input_tokens"]
    max_ground_truth_tokens = evaluation_data_length["max_ground_truth_tokens"]
    max_input_characters = evaluation_data_length["max_input_characters"]
    max_ground_truth_characters = evaluation_data_length["max_ground_truth_characters"]

    # Get applicable llms
    applicable_llms = llm_applicability.get_applicable_llms(
        max_input_tokens=max_input_tokens,
        max_ground_truth_tokens=max_ground_truth_tokens,
        max_input_characters=max_input_characters,
        max_ground_truth_characters=max_ground_truth_characters,
    )

    # Check that at least one llm is applicable
    if len(applicable_llms) == 0:
        raise AssertionError(
            "Input and output data length exceed context length of available LLMs."
        )

    # Check that text-davinci-003 is an applicable LLM and that at least 3 few shot examples fit (needed for prompt generation)
    if (
        "text-davinci-003" not in applicable_llms
        or applicable_llms["text-davinci-003"]["max_few_shots"] < 3
    ):
        raise AssertionError(
            "Input and output data length exceed context length of available LLMs (assumes few shot examples are used)."
        )


def check_evaluation_dataset(
    dataset_file_path: str, synthetic_data_generation: bool = False
) -> None:
    """Checks contents of evaluation dataset for potential errors.

    Does not validate if data lengths exceed llm token limits.

    Args:
        dataset_file_path (str): file path to evaluation dataset.
        synthetic_data_generation (bool, optional): whether this task request is to generate synthetic data. Defaults to False.

    Raises:
        AssertionError: file size is >1 MB.
        AssertionError: file type is not csv.
        AssertionError: insufficient rows of data (must have at least 1 row plus column headers).
        AssertionError: insufficient rows of data for Task creation (must have at least 15 rows of data).
        AssertionError: insufficient number of columns (must have at least 1).
        AssertionError: improper naming of input variables (must be alphanumeric + underscores, no spaces).
        AssertionError: duplicate input variable names.
        AssertionError: duplicate rows of data.
    """
    # Check that evaluation data is at most 1 MB file size
    if os.path.getsize(dataset_file_path) > 1000000:
        raise AssertionError("Evaluation dataset can be at most 1 MB large.")

    # Try to import evaluation dataset
    try:
        csvfile = open(dataset_file_path, newline="")
        data = list(csv.reader(csvfile))
    except:
        raise AssertionError(
            "Could not import evaluation data. Make sure to upload in csv format."
        )

    # Check that there is at least 1 row of evaluation data
    if len(data) < 2:
        raise AssertionError(
            "There must be at least 1 row of evaluation data plus column headers."
        )

    # For Task creation request and not synthetic data generation, check that there is at least 15 rows of data
    if (not synthetic_data_generation) and len(data) < 16:
        raise AssertionError("There must be at least 15 rows of evaluation data.")

    # Check that there is at least 1 column. Last column is assumed to be the ground truth
    columns = data[0]
    if len(columns) == 0:
        raise AssertionError(
            "There must be at least 1 column. The rightmost column is assumed to be the ground truth."
        )

    # Check that each input variable is a single non-empty string with letters, numbers, and underscores only (no spaces)
    input_variables = columns[:-1]
    for input_var in input_variables:
        if not re.match(r"^[A-Za-z0-9_]+$", input_var):
            raise AssertionError(
                "Input variable names must be a single string letters, numbers, and underscores only (no spaces allowed)."
            )

    # Check that there are no duplicate input variable names
    if len(input_variables) != len(set(input_variables)):
        raise AssertionError("Input variable names must be unique.")

    # Check that there are no duplicate rows
    seen_rows = set()
    for row in data[1:]:
        row_csv = ",".join(row)
        if row_csv in seen_rows:
            raise AssertionError("Data cannot have duplicate rows.")
        else:
            seen_rows.add(row_csv)


def get_evaluation_dataset(
    dataset_file_path: str, escape_curly_braces: bool = True
) -> pd.DataFrame:
    """Convert evaluation dataset csv into DataFrame.

    Assumes evaluation dataset has been checked appropriately. Escapes curly braces for use with format strings by adding extra curly
        brace (e.g., converts '{'  to '{{').

    Args:
        dataset_file_path (str): file path to evaluation dataset.
        escape_curly_braces (bool, optional): whether to escape curly braces when getting data lengths. Defaults to True.

    Returns:
        pd.DataFrame: processed evaluation dataset.
    """
    # Import evaluation dataset
    csvfile = open(dataset_file_path, newline="")
    data = list(csv.reader(csvfile))

    # Rename each input variable by prepending "var_" (to avoid duplicating with columns names in internal DataFrames)
    columns = data[0]
    columns[:-1] = [f"var_{input_var}" for input_var in columns[:-1]]

    # Rename last column to "ground_truth" in case it is not already named as such
    columns[-1] = "ground_truth"

    # Convert dataset to DataFrame and shuffle data
    evaluation_dataset = (
        pd.DataFrame(data=data[1:], columns=columns)
        .sample(frac=1)
        .reset_index(drop=True)
    )

    # Escape curly braces
    if escape_curly_braces:
        evaluation_dataset = evaluation_dataset.applymap(
            lambda x: x.replace("{", "{{").replace("}", "}}")
        )

    # Add evaluation_data_id column
    evaluation_dataset["evaluation_data_id"] = evaluation_dataset.index

    # Return processed evaluation dataset
    return evaluation_dataset
