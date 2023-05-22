"""Helper functions to return appropriate llm for each step in synthetic data generation algorithm."""

from app.models.component.task_request import TaskRequest
from app.models.llm.factory import LLMFactory
from app.models.llm.base import BaseLLM


def get_categorization_llm(openai_api_key: str) -> BaseLLM:
    """Returns llm to categorize each evaluation data point.

    Args:
        openai_api_key (str): OpenAI API key to use.

    Returns:
        BaseLLM: llm to use.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.4,
        "max_tokens": 500,
        "openai_api_key": openai_api_key,
    }

    # Create the model instance
    model = LLMFactory.create_llm("openai", **model_params)

    return model


def get_category_generation_llm(openai_api_key: str) -> BaseLLM:
    """Returns llm to use to generate new categories for synthetic data points.

    Args:
        openai_api_key (str): OpenAI API key to use.

    Returns:
        BaseLLM: llm to use.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.7,
        "max_tokens": 500,
        "openai_api_key": openai_api_key,
    }

    # Create the model instance
    model = LLMFactory.create_llm("openai", **model_params)

    return model


def get_synthetic_data_generation_model(
    task_request: TaskRequest, openai_api_key: str
) -> BaseLLM:
    """Returns llm to use to generate synthetic data.

    Args:
        task_request (TaskRequest): details for this task creation run.
        openai_api_key (str): OpenAI API key to use.

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
        "openai_api_key": openai_api_key,
    }

    # Create the model instance
    model = LLMFactory.create_llm("openai", **model_params)

    return model
