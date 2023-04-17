"""Helper functions to return appropriate llm for each step in synthetic data generation algorithm."""

from app.models.component.task_request import TaskRequest
from app.models.llm.factory import LLMFactory
from app.models.llm.base import BaseLLM


def get_categorization_llm() -> BaseLLM:
    """Returns llm to categorize each evaluation data point.

    Returns:
        BaseLLM: llm to use.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.4,
        "max_tokens": 500,
    }

    # Create the model instance
    llm_factory = LLMFactory()
    model = llm_factory.create_llm("openai", **model_params)

    return model


def get_category_generation_llm() -> BaseLLM:
    """Returns llm to use to generate new categories for synthetic data points.

    Returns:
        BaseLLM: llm to use.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.7,
        "max_tokens": 500,
    }

    # Create the model instance
    llm_factory = LLMFactory()
    model = llm_factory.create_llm("openai", **model_params)

    return model


def get_synthetic_data_generation_model(task_request: TaskRequest) -> BaseLLM:
    """Returns llm to use to generate synthetic data.

    Args:
        task_request (TaskRequest): details for this task creation run.

    Returns:
        BaseLLM: llm to use.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.7,
        "max_tokens": task_request.applicable_llms["text-davinci-003"][
            "max_few_shot_example_length"
        ],
    }

    # Create the model instance
    llm_factory = LLMFactory()
    model = llm_factory.create_llm("openai", **model_params)

    return model
