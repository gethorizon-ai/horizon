"""Contains helper functions to process and extract info from evaluation dataset."""

from . import data_length
from . import llm_applicability
import os
import csv
import re
import pandas as pd
from typing import List
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)

# CHUNK_SIZE = 1000
# CHUNK_OVERLAP = 0


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

    # Check that text-davinci-003 is an applicable LLM (needed for prompt generation)
    if "text-davinci-003" not in applicable_llms:
        raise AssertionError(
            "Input and output data length exceed context length of available LLMs needed for prompt generation."
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
        AssertionError: cells exist that are empty or only have whitespace.
        AssertionError: improper naming of input variables (must be alphanumeric + underscores, no spaces).
        AssertionError: duplicate input variable names.
        AssertionError: duplicate rows of data.
    """
    # Check that evaluation data is at most 50 MB file size
    if os.path.getsize(dataset_file_path) > 50000000:
        raise AssertionError("Evaluation dataset can be at most 50 MB large.")

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
            "Detected less than 2 rows of data. There must be at least 1 row of evaluation data plus column headers."
        )

    # For Task creation request and not synthetic data generation, check that there is at least 15 rows of data
    if (not synthetic_data_generation) and len(data) < 16:
        raise AssertionError(
            "Detected less than 15 rows of data. There must be at least 15 rows of evaluation data plus column headers."
        )

    # Check that there is at least 1 column. Last column is assumed to be the ground truth
    columns = data[0]
    if len(columns) == 0:
        raise AssertionError(
            "Detected no column headers (first row of csv file). There must be at least 1 column. The rightmost column is assumed to be the ground truth."
        )

    # Check that there are no cells that are empty or only have whitespace
    for i, row in enumerate(data):
        for j, cell in enumerate(row):
            if cell.strip() == "":
                raise AssertionError(
                    f"Detected empty or whitespace cell at row {i+1}, column {j+1}. Please try again with data where each cell has text. For example, check that there are no empty rows or columns bordering the data."
                )

    # Check that each input variable is a single non-empty string with letters, numbers, and underscores only (no spaces)
    input_variables = columns[:-1]
    for index, input_var in enumerate(input_variables):
        if not re.match(r"^[A-Za-z0-9_]+$", input_var):
            raise AssertionError(
                f"Could not read input variable name at column {index+1} ({input_var}). Input variable names must be in the first row of the CSV file. Each input variable name must be composed of letters, numbers, and underscores only (no spaces or empty values allowed)."
            )

    # Check that there are no duplicate input variable names
    seen_variables = set()
    duplicates = []
    for variable in input_variables:
        if variable in seen_variables:
            duplicates.append(variable)
        else:
            seen_variables.add(variable)
    if duplicates:
        error_message = "Detected duplicate input variable names: "
        for duplicate in duplicates:
            error_message += f"{duplicate} (column {columns.index(duplicate) + 1}), "
        error_message = error_message.rstrip(", ")
        error_message += ". Please try again with unique input variable names."
        raise AssertionError(error_message)

    # Check that there are no duplicate rows
    seen_rows = set()
    for i, row in enumerate(
        data[1:], start=2
    ):  # Start at index 2 to account for header row
        row_csv = ",".join(row)
        if row_csv in seen_rows:
            raise AssertionError(
                f"Detected duplicate rows of data. Please try again with unique rows of data. Duplicate row found at line {i}."
            )
        else:
            seen_rows.add(row_csv)


def get_evaluation_dataset(
    dataset_file_path: str,
    escape_curly_braces: bool = True,
    input_variables_to_chunk: List[str] = None,
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

    # Chunk input variables if required
    if input_variables_to_chunk:
        pass

        # # TODO:
        # # Ensure that input_variables_to_chunk are all valid columns in raw_dataset
        # assert all(
        #     var in evaluation_dataset.columns.to_list()
        #     for var in input_variables_to_chunk
        # )

        # # Setup text splitter
        # text_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        # )

        # # Chunk each input variable
        # for var in input_variables_to_chunk:
        #     evaluation_dataset[var] = evaluation_dataset[var].apply(
        #         lambda x: text_splitter.split_text(x)
        #     )
        #     evaluation_dataset = evaluation_dataset.explode(var)
        #     evaluation_dataset = evaluation_dataset.reset_index(drop=True)

    # Return processed evaluation dataset
    return evaluation_dataset
