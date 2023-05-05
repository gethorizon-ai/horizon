"""Generates synthetic data for the user to curate and edit to enlarge their dataset."""

from app.models.component.task_request import TaskRequest
from app.models.prompt.factory import PromptTemplateFactory
from app.models.prompt.prompt import PromptTemplate
from app.models.llm.factory import LLMFactory
from app.models.llm.base import BaseLLM
from app.utilities.synthetic_data import prompts
from app.utilities.synthetic_data import models
import pandas as pd
import json


def generate_synthetic_data(
    task_request: TaskRequest, num_synthetic_data: int
) -> pd.DataFrame:
    """Given the current evaluation dataset, generates synthetic data for the user to curate and edit to enlarge their dataset.

    Algorithm first categorizes each evaluation data point, then generates new categories for synthetic data, and finally generates
    synthetic data based on the existing examples and new categories.

    Args:
        task_request (TaskRequest): details for this task creation run.
        num_synthetic_data (int): number of synthetic data points to generate.

    Raises:
        ValueError: in case algorithm fails to generate synthetic dataset.

    Returns:
        pd.DataFrame: synthetic dataset, with values for each input variable and ground truth.
    """
    pass

    # Ensure evaluation dataset has some initial data
    assert len(task_request.evaluation_data) > 1
    assert num_synthetic_data > 0

    # Create list of dicts for each evaluation data point (i.e., JSON format)
    evaluation_data_dict = task_request.evaluation_dataset.drop(
        "evaluation_data_id", axis=1
    ).to_dict(orient="records")

    # Categorize each evaluation data point
    prompt_category = prompts.get_categorization_prompt(task_request=task_request)
    llm_category = models.get_categorization_llm()
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

    # Generate category labels for synthetic data
    max_tries = 3
    new_categories = []
    prompt_category_generation = prompts.get_category_generation_prompt()
    prompt_category_generation_formatted = prompt_category_generation.format(
        num_synthetic_data=num_synthetic_data,
        category_labels="\n".join(category_labels),
    )
    llm_category_generation = models.get_category_generation_llm()
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
        prompts.get_synthetic_data_generation_prompt_suffix()
    )
    llm_synthetic_data_generation = models.get_synthetic_data_generation_model(
        task_request=task_request
    )

    num_few_shots = min(
        5,
        len(task_request.evaluation_dataset),
        task_request.applicable_llms["text-davinci-003"]["max_few_shots"],
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
                        **evaluation_data_dict[(i + j) % len(evaluation_data_dict)]
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
                synthetic_data_generations.append(json.loads(response))
                break
            except:
                continue

    # Convert synthetic data examples to DataFrame
    synthetic_data = pd.DataFrame(synthetic_data_generations)

    # Remove "var_" prepending each input variable name
    synthetic_data.columns = [
        input_variable[4:] for input_variable in synthetic_data.columns[:-1]
    ] + synthetic_data.columns[-1:]

    return synthetic_data
