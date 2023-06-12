"""Defines helper methods to determine applicable llms for task."""

from app.models.llm.factory import LLMFactory
from app.utilities.dataset_processing import chunk


def get_applicable_llms(
    max_input_tokens: int,
    max_ground_truth_tokens: int,
    max_input_characters: int,
    max_ground_truth_characters: int,
    include_context_from_data_repository: bool = False,
) -> dict:
    """Determines applicable models and associated parameters for given evaluation data.

    Args:
        max_input_tokens (int): max number of tokens used for input data in evaluation dataset.
        max_ground_truth_tokens (int): max number of tokens used for ground truth data in evaluation dataset.
        max_input_characters (int): max number of characters used for input data in evaluation dataset.
        max_ground_truth_characters (int): max number of characters used for ground truth data in evaluation dataset.
        include_context_from_data_repository (bool, optional): whether to incorporate length of context from data repository.
            Defaults to False

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

    # If applicable, incorporate context from data repository for QA use case
    if include_context_from_data_repository:
        zero_shot_tokens += (
            chunk.MAX_DATA_REPOSITORY_CONTEXT_LENGTH
            * LLMFactory.llm_data_assumptions["tokens_per_character"]
        )
        zero_shot_characters += chunk.MAX_DATA_REPOSITORY_CONTEXT_LENGTH

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
