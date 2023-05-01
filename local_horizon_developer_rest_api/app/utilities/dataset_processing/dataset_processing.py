"""Contains helper functions to process and extract info from evaluation dataset."""

from app.models.llm.factory import LLMFactory
from app.models.llm.open_ai import OpenAI, ChatOpenAI
from app.models.llm.anthropic import ChatAnthropic
import os
import csv
import re
import pandas as pd
from typing import List


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
    evaluation_dataset = get_evaluation_dataset(dataset_file_path=dataset_file_path)

    # Check that evaluation data lengths are appropriate
    evaluation_data_length = get_evaluation_data_length(
        evaluation_dataset=evaluation_dataset
    )
    max_input_tokens = evaluation_data_length["max_input_tokens"]
    max_ground_truth_tokens = evaluation_data_length["max_ground_truth_tokens"]
    max_input_characters = evaluation_data_length["max_input_characters"]
    max_ground_truth_characters = evaluation_data_length["max_ground_truth_characters"]

    # Get applicable llms
    applicable_llms = get_applicable_llms(
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
    try:
        if os.path.getsize(dataset_file_path) > 1000000:
            raise AssertionError("Evaluation dataset can be at most 1 MB large.")
    except Exception as e:
        raise AssertionError(
            f"Got the following error when trying to acccess evaluation dataset: {str(e)}"
        )

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


def get_evaluation_dataset(dataset_file_path: str) -> pd.DataFrame:
    """Convert evaluation dataset csv into DataFrame.

    Assumes evaluation dataset has been checked appropriately.

    Args:
        dataset_file_path (str): file path to evaluation dataset.

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

    # Add evaluation_data_id column
    evaluation_dataset["evaluation_data_id"] = evaluation_dataset.index

    # Return processed evaluation dataset
    return evaluation_dataset


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


def get_evaluation_data_length(
    evaluation_dataset: pd.DataFrame,
) -> dict:
    """Determines max count of tokens and characters across input and ground truth data.

    Assumes evaluation dataset has been checked and processed appropriately.

    Args:
        evaluation_dataset (pd.DataFrame): checked and processed evaluation dataset.

    Raises:
        AssertionError: task_request must have evaluation dataset.

    Returns:
        dict: max tokens and characters for input and ground truth data.
    """
    # Drop evaluation_data_id column
    evaluation_dataset_analysis = evaluation_dataset.drop("evaluation_data_id", axis=1)

    # Separate input and ground truth data
    input_data_analysis = evaluation_dataset_analysis.iloc[:, :-1]
    ground_truth_data_analysis = evaluation_dataset_analysis.iloc[:, -1:]

    # Calculate data length used for input values and ground truth for each row based on
    # count of tokens and characters. Use max value of different encodings to be conservative
    def count_tokens(row: dict):
        string = "\n".join([f"<{key}>: {value}" for key, value in row.items()])
        token_count = max(
            OpenAI.get_data_length(string),
            ChatOpenAI.get_data_length(string),
            ChatAnthropic.get_data_length(string),
        )
        return token_count

    def count_chars(row: dict):
        string = "\n".join([f"<{key}>: {value}" for key, value in row.items()])
        char_count = len(string)
        return char_count

    max_input_tokens = input_data_analysis.apply(
        lambda row: count_tokens(row.to_dict()), axis=1
    ).max()
    max_ground_truth_tokens = ground_truth_data_analysis.apply(
        lambda row: count_tokens(row.to_dict()), axis=1
    ).max()
    max_input_characters = input_data_analysis.apply(
        lambda row: count_chars(row.to_dict()), axis=1
    ).max()
    max_ground_truth_characters = ground_truth_data_analysis.apply(
        lambda row: count_chars(row.to_dict()), axis=1
    ).max()

    # Correct for fact that "<OUTPUT>:" is part of prompt, while "<ground_truth>: " is not part of LLM completion
    output_string = "\n<OUTPUT>:"
    ground_truth_string = "\n<ground_truth>: "
    max_input_tokens += max(
        OpenAI.get_data_length(output_string),
        ChatOpenAI.get_data_length(output_string),
        ChatAnthropic.get_data_length(output_string),
    )
    max_ground_truth_tokens -= min(
        OpenAI.get_data_length(ground_truth_string),
        ChatOpenAI.get_data_length(ground_truth_string),
        ChatAnthropic.get_data_length(ground_truth_string),
    )
    max_input_characters += len(output_string)
    max_ground_truth_characters -= len(ground_truth_string)

    # Return max data lengths
    return {
        "max_input_tokens": max_input_tokens,
        "max_ground_truth_tokens": max_ground_truth_tokens,
        "max_input_characters": max_input_characters,
        "max_ground_truth_characters": max_ground_truth_characters,
    }


def get_applicable_llms(
    max_input_tokens: int,
    max_ground_truth_tokens: int,
    max_input_characters: int,
    max_ground_truth_characters: int,
) -> dict:
    """Determines applicable models and associated parameters for given evaluation data.

    Args:
        max_input_tokens (int): max number of tokens used for input data in evaluation dataset.
        max_ground_truth_tokens (int): max number of tokens used for ground truth data in evaluation dataset.
        max_input_characters (int): max number of characters used for input data in evaluation dataset.
        max_ground_truth_characters (int): max number of characters used for ground truth data in evaluation dataset.

    Raises:
        AssertionError: task_request must have evaluation dataset length statistics.

    Returns:
        dict: applicable models and associated parameters (e.g., max few shots).
    """
    if (
        max_input_tokens == None
        or max_ground_truth_tokens == None
        or max_input_characters == None
        or max_ground_truth_characters == None
    ):
        raise AssertionError(
            "Must compute evalution dataset length statistics first before determining applicable llms."
        )

    # Determine max data length of llm output
    max_output_tokens = int(
        max(
            LLMFactory.llm_data_assumptions["min_max_output_tokens"],
            max_ground_truth_tokens
            * LLMFactory.llm_data_assumptions["input_output_multiplier"],
        )
    )
    max_output_characters = int(
        max(
            LLMFactory.llm_data_assumptions["min_max_output_tokens"],
            max_ground_truth_characters
            * LLMFactory.llm_data_assumptions["input_output_multiplier"],
        )
    )

    # Determine data length of zero-shot prompt, including llm output
    zero_shot_tokens = int(
        LLMFactory.llm_data_assumptions["buffer_tokens"]
        + LLMFactory.llm_data_assumptions["instruction_tokens"]
        + (
            max_input_tokens
            * LLMFactory.llm_data_assumptions["input_output_multiplier"]
        )
        + max_output_tokens
    )
    zero_shot_characters = int(
        LLMFactory.llm_data_assumptions["buffer_characters"]
        + LLMFactory.llm_data_assumptions["instruction_characters"]
        + (
            max_input_characters
            * LLMFactory.llm_data_assumptions["input_output_multiplier"]
        )
        + max_output_characters
    )

    # Determine data length of single few shot example
    max_few_shot_example_tokens = int(
        (max_input_tokens * LLMFactory.llm_data_assumptions["input_output_multiplier"])
        + max_output_tokens
    )
    max_few_shot_example_characters = int(
        (
            max_input_characters
            * LLMFactory.llm_data_assumptions["input_output_multiplier"]
        )
        + max_output_characters
    )

    applicable_llms = {}
    for llm, llm_info in LLMFactory.llm_classes.items():
        if llm_info["data_unit"] == "token":
            if zero_shot_tokens > llm_info["data_limit"]:
                continue
            tokens_left_for_few_shots = llm_info["data_limit"] - zero_shot_tokens
            # Assume up to 10 few shot examples
            max_few_shots = min(
                LLMFactory.llm_data_assumptions["max_few_shots"],
                tokens_left_for_few_shots // max_few_shot_example_tokens,
            )
            applicable_llms[llm] = {
                "max_few_shots": max_few_shots,
                "max_few_shot_example_length": max_few_shot_example_tokens,
                "max_output_length": max_output_tokens,
            }
        elif llm_info["data_unit"] == "character":
            if zero_shot_characters > llm_info["data_limit"]:
                continue
            characters_left_for_few_shots = (
                llm_info["data_limit"] - zero_shot_characters
            )
            # Assume up to 10 few shot examples
            max_few_shots = min(
                10, characters_left_for_few_shots // max_few_shot_example_characters
            )
            applicable_llms[llm] = {
                "max_few_shots": max_few_shots,
                "max_few_shot_example_length": max_few_shot_example_characters,
                "max_output_length": max_output_characters,
            }

    # Return applicable_llms
    return applicable_llms


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

    # Assume 80/20 split with at least 5 and at most 10 training data points
    num_train_data = min(10, max(5, int(len(evaluation_dataset) * 0.2)))

    # Assume at most 15 test data points
    num_test_data = min(15, len(evaluation_dataset) - num_train_data)

    # Use num_test_data input value if provided
    if num_test_data_input != None:
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
