"""Defines helper functions to assess data length in evaluation dataset."""

from app.models.llm.open_ai import OpenAI, ChatOpenAI
from app.models.llm.anthropic import ChatAnthropic
import pandas as pd


def get_evaluation_data_length(
    evaluation_dataset: pd.DataFrame,
    unescape_characters: bool = True,
) -> dict:
    """Determines max count of tokens and characters across input and ground truth data.

    Assumes evaluation dataset has been checked and processed appropriately.

    Args:
        evaluation_dataset (pd.DataFrame): checked and processed evaluation dataset.
        unescape_characters (bool, optional): whether to unescape certain characters (e.g., curly braces) when getting data lengths.
            Defaults to True.

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
        if unescape_characters:
            string.replace("{{", "{").replace("}}", "}")
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
