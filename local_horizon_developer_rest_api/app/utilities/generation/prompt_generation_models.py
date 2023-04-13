"""Generates LLMs for use with each prompt generation method."""

from app.models.llm.factory import LLMFactory
from app.models.llm.base import BaseLLM


def get_model_user_objective(num_prompts: int) -> BaseLLM:
    """Returns llm for use with prompt generation with user objective.

    Args:
        num_prompts (int): number of prompts that llm should generate.

    Returns:
        BaseLLM: llm to generate prompts.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.4,
        "max_tokens": 1500,
        "n": num_prompts,
        "best_of": num_prompts,
    }

    # Create the model instance
    llm_factory = LLMFactory()
    metaprompt_model = llm_factory.create_llm("text-davinci-003", **model_params)

    return metaprompt_model


def get_model_user_objective_training_data(num_prompts: int) -> BaseLLM:
    """Returns llm for use with prompt generation with user objective and training data.

    Args:
        num_prompts (int): number of prompts that llm should generate.

    Returns:
        BaseLLM: llm to generate prompts.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.4,
        "max_tokens": 1000,
        "n": num_prompts,
        "best_of": num_prompts,
    }

    # Create the model instance
    llm_factory = LLMFactory()
    metaprompt_model = llm_factory.create_llm("text-davinci-003", **model_params)

    return metaprompt_model


def get_model_pattern_role_play(num_prompts: int) -> BaseLLM:
    """Returns llm for use with prompt generation with role play pattern.

    Args:
        num_prompts (int): number of prompts that llm should generate.

    Returns:
        BaseLLM: llm to generate prompts.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.4,
        "max_tokens": 1500,
        "n": num_prompts,
        "best_of": num_prompts,
    }

    # Create the model instance
    llm_factory = LLMFactory()
    metaprompt_model = llm_factory.create_llm("text-davinci-003", **model_params)

    return metaprompt_model


def get_model_variants(num_prompts: int) -> BaseLLM:
    """Returns llm for use with prompt generation through variants.

    Args:
        num_prompts (int): number of prompts that llm should generate.

    Returns:
        BaseLLM: llm to generate prompts.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.9,
        "max_tokens": 1500,
        "n": num_prompts,
        "best_of": num_prompts,
    }

    # Create the model instance
    llm_factory = LLMFactory()
    metaprompt_model = llm_factory.create_llm("text-davinci-003", **model_params)

    return metaprompt_model


def get_model_variants_check() -> BaseLLM:
    """Returns llm to check prompt generation through variants.

    Returns:
        BaseLLM: llm to check newly generated prompts.
    """
    # Define the prompt template factory instance
    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.3,
        "max_tokens": 1000,
    }

    # Create the model instance
    llm_factory = LLMFactory()
    metaprompt_model = llm_factory.create_llm("text-davinci-003", **model_params)

    return metaprompt_model
