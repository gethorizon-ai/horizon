"""Generates synthetic data for the user to curate and edit to enlarge their dataset."""

from app.models.component.task_request import TaskRequest
from app.utilities.synthetic_data import prompts
from app.utilities.synthetic_data import models
from app.utilities.S3.s3_util import upload_file_to_s3
import pandas as pd
import json
import os
from io import BytesIO
from datetime import datetime


# Assume only usage of text-davinci-003 for synthetic data generation
ALLOWED_MODELS = ["text-davinci-003"]


def generate_synthetic_data(
    user_objective: str,
    dataset_s3_key: str,
    num_synthetic_data: int,
    openai_api_key: str,
) -> str:
    """Given the original evaluation dataset, generates synthetic data for the user to curate and edit to enlarge their dataset.

    Algorithm first categorizes each evaluation data point, then generates new categories for synthetic data, and finally generates
    synthetic data based on the existing examples and new categories. Inspired by this paper - https://arxiv.org/abs/2203.14465.

    Args:
        user_objective (str): objective of the use case.
        dataset_s3_key (str): s3 key to fetch original dataset.
        num_synthetic_data (int): number of synthetic data points to generate.
        openai_api_key (str): OpenAI API key to use.

    Raises:
        ValueError: in case algorithm fails to generate synthetic dataset.

    Returns:
        str: s3 key to synthetic dataset.
    """
    if user_objective == None or len(user_objective) == 0 or len(user_objective) > 500:
        raise ValueError("Must provide user objective with at most 500 characters.")

    # Get the evaluation dataset. If there is no evaluation dataset, return an error
    if not dataset_s3_key:
        raise AssertionError("No evaluation dataset associated with this task.")

    if num_synthetic_data <= 0 or num_synthetic_data > 50:
        raise ValueError(
            "Number of synthetic data points to generate must be between 1-50."
        )

    # Create the TaskRequest instance
    task_request = TaskRequest(
        dataset_s3_key=dataset_s3_key,
        user_objective=user_objective,
        allowed_models=ALLOWED_MODELS,
    )

    # Check that valid API key is provided
    task_request.check_relevant_api_keys(openai_api_key=openai_api_key)

    # Create list of dicts for each evaluation data point (i.e., JSON format)
    # Use min of number of data points and synthetic data points requested
    num_data_points = min(len(task_request.evaluation_dataset), num_synthetic_data)
    evaluation_data_dict = (
        task_request.evaluation_dataset.drop("evaluation_data_id", axis=1)
        .head(num_data_points)
        .to_dict(orient="records")
    )

    # Categorize each evaluation data point
    prompt_category = prompts.get_categorization_prompt(task_request=task_request)
    llm_category = models.get_categorization_llm(openai_api_key=openai_api_key)
    category_labels = []
    for i in range(len(evaluation_data_dict)):
        prompt_category_formatted = prompt_category.format(**evaluation_data_dict[i])
        category = (
            llm_category.generate([prompt_category_formatted])
            .generations[0][0]
            .text.strip()
        )
        category_labels.append(category)
    assert len(category_labels) == len(evaluation_data_dict)
    print(f"Category labels: {category_labels}")

    # Generate category labels for synthetic data
    max_tries = 3
    new_categories = []
    prompt_category_generation = prompts.get_category_generation_prompt()
    prompt_category_generation_formatted = prompt_category_generation.format(
        num_synthetic_data=num_synthetic_data,
        category_labels="\n".join(category_labels),
    )
    llm_category_generation = models.get_category_generation_llm(
        openai_api_key=openai_api_key
    )
    for i in range(max_tries):
        try:
            new_categories = (
                llm_category_generation.generate([prompt_category_generation_formatted])
                .generations[0][0]
                .text.strip()
                .split("\n")
            )
            assert len(new_categories) == num_synthetic_data
            break
        except:
            continue

    if len(new_categories) == 0:
        raise ValueError("Couldn't generate new category labels.")
    print(f"New categories: {new_categories}")

    # Generate synthetic data
    prompt_prefix_synthetic_data_generation = (
        prompts.get_synthetic_data_generation_prompt_prefix()
    )
    prompt_prefix_synthetic_data_generation_formatted = (
        prompt_prefix_synthetic_data_generation.format(
            user_objective=task_request.user_objective
        )
    )
    prompt_synthetic_data_generation_example = (
        prompts.get_synthetic_data_generation_example_prompt(task_request=task_request)
    )
    prompt_suffix_synthetic_data_generation = (
        prompts.get_synthetic_data_generation_prompt_suffix(task_request=task_request)
    )
    llm_synthetic_data_generation = models.get_synthetic_data_generation_model(
        task_request=task_request, openai_api_key=openai_api_key
    )

    num_few_shots = min(
        len(task_request.evaluation_dataset),
        task_request.applicable_llms["text-davinci-003"]["max_few_shots"],
        5,
    )
    synthetic_data_generations = []
    for i in range(num_synthetic_data):
        max_tries = 3
        for iter in range(max_tries):
            prompt_synthetic_data_formatted = (
                prompt_prefix_synthetic_data_generation_formatted
            )

            for j in range(num_few_shots):
                prompt_synthetic_data_formatted += (
                    prompt_synthetic_data_generation_example.format(
                        category=category_labels[(i + j) % len(category_labels)],
                        **evaluation_data_dict[(i + j) % len(evaluation_data_dict)],
                    )
                )
            prompt_synthetic_data_formatted += (
                prompt_suffix_synthetic_data_generation.format(
                    new_category=new_categories[i]
                )
            )

            response = (
                llm_synthetic_data_generation.generate(
                    [prompt_synthetic_data_formatted]
                )
                .generations[0][0]
                .text.strip()
            )
            try:
                # Check that response matches schema of evaluation dataset
                result = json.loads(response, strict=False)
                assert check_dict_keys(
                    dictionary=result,
                    key_list=task_request.input_variables + ["OUTPUT"],
                )
                print(f"Synthetic data generated: {str(result)}")
                synthetic_data_generations.append(result)
                break
            except:
                continue

    # Convert synthetic data examples to DataFrame
    synthetic_data = pd.DataFrame(synthetic_data_generations)

    # Remove "var_" prepending each input variable name
    new_columns = [input_variable[4:] for input_variable in synthetic_data.columns[:-1]]
    new_columns.extend(synthetic_data.columns[-1:])
    synthetic_data.columns = new_columns

    # Upload synthetic data to s3 as csv
    csv_buffer = BytesIO()
    synthetic_data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    synthetic_dataset_s3_key = f"synthetic_data_generation/synthetic_datasets/{datetime.now().strftime('%Y/%m/%d/%H%M%SZ')}/{os.path.basename(dataset_s3_key)}"
    upload_file_to_s3(file=csv_buffer, key=synthetic_dataset_s3_key)

    # Return s3 key
    return synthetic_dataset_s3_key


def check_dict_keys(dictionary: dict, key_list: list) -> bool:
    """Checks that the keys of dict exactly matches an expected list of keys.

    Args:
        dictionary (dict): dictionary to check keys.
        key_list (list): expected list of keys.

    Returns:
        bool: whether keys of dict exactly matches expected list of keys.
    """
    dict_keys = list(dictionary.keys())
    dict_keys.sort()  # Sort the dictionary keys for comparison
    key_list.sort()  # Sort the list of keys for comparison
    return dict_keys == key_list
