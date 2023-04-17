"""Test prompt generation methods."""

from app.models.llm.factory import LLMFactory
from app.models.component import TaskRequest
from app.utilities.generation import user_objective
from app.utilities.generation import pattern_role_play
from app.utilities.generation import user_objective_training_data
from app.utilities.generation import variants
from app.utilities.generation import few_shot
from app.utilities.generation import temperature_variation
import pytest
import os
from dotenv import load_dotenv
import openai


def test_prompt_generation_user_objective():
    """Test prompt generation with user objective."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    task_request = TaskRequest(
        user_objective="generate a marketing email",
        dataset_file_path="./data/email_gen_demo.csv",
        num_test_data_input=2,
    )

    print("User Objective:", task_request.user_objective)
    print("Input Variables:", task_request.input_variables)

    llm_factory = LLMFactory()

    # Define the OpenAI instance parameters
    openai_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.4,
        "max_tokens": task_request.max_ground_truth_tokens,
    }

    # Create the OpenAI instance
    openai_instance = llm_factory.create_llm(
        openai_params["model_name"], **openai_params
    )

    print("OpenAI instance:", openai_instance)

    num_prompts = 1
    starting_prompt_model_id = 1
    result = user_objective.prompt_generation_user_objective(
        task_request=task_request,
        model_object=openai_instance,
        num_prompts=num_prompts,
        starting_prompt_model_id=starting_prompt_model_id,
    )
    assert len(result) > 0, "No prompts generated"
    assert len(result) <= num_prompts, "Generated more prompts than expected"

    for index, row in result.iterrows():
        assert row["prompt_model_id"] is not None, "Prompt-model ID is missing"
        assert row["generation_id"] == "[user_objective]", "Incorrect generation_id"
        assert row["prompt_object"] is not None, "Prompt object is missing"
        assert row["prompt_prefix"] is not None, "Prompt prefix is missing"
        assert row["model_object"] is not None, "Model object is missing"


def test_prompt_generation_pattern_role_play():
    """Test prompt generation with role play pattern."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    task_request = TaskRequest(
        user_objective="generate a marketing email",
        dataset_file_path="./data/email_gen_demo.csv",
        num_test_data_input=2,
    )

    print("User Objective:", task_request.user_objective)
    print("Input Variables:", task_request.input_variables)

    llm_factory = LLMFactory()

    # Define the OpenAI instance parameters
    openai_params = {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.4,
        "max_tokens": task_request.max_ground_truth_tokens,
    }

    # Create the OpenAI instance
    openai_instance = llm_factory.create_llm(
        openai_params["model_name"], **openai_params
    )

    print("OpenAI instance:", openai_instance)

    num_prompts = 1
    starting_prompt_model_id = 1
    result = pattern_role_play.prompt_generation_pattern_role_play(
        task_request=task_request,
        model_object=openai_instance,
        num_prompts=num_prompts,
        starting_prompt_model_id=starting_prompt_model_id,
    )
    assert len(result) > 0, "No prompts generated"
    assert len(result) <= num_prompts, "Generated more prompts than expected"

    for index, row in result.iterrows():
        assert row["prompt_model_id"] is not None, "Prompt-model ID is missing"
        assert row["generation_id"] == "[pattern_role_play]", "Incorrect generation_id"
        assert row["prompt_object"] is not None, "Prompt object is missing"
        assert row["prompt_prefix"] is not None, "Prompt prefix is missing"
        assert row["model_object"] is not None, "Model object is missing"


def test_prompt_generation_user_objective_training_data():
    """Test prompt generation with user objective and training data."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    task_request = TaskRequest(
        user_objective="generate a marketing email",
        dataset_file_path="./data/email_gen_demo.csv",
        num_test_data_input=2,
    )

    print("User Objective:", task_request.user_objective)
    print("Input Variables:", task_request.input_variables)

    llm_factory = LLMFactory()

    # Define the OpenAI instance parameters
    openai_params = {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.4,
        "max_tokens": task_request.max_ground_truth_tokens,
    }

    # Create the OpenAI instance
    openai_instance = llm_factory.create_llm(
        openai_params["model_name"], **openai_params
    )

    print("OpenAI instance:", openai_instance)

    num_prompts = 1
    starting_prompt_model_id = 1
    result = (
        user_objective_training_data.prompt_generation_user_objective_training_data(
            task_request=task_request,
            model_object=openai_instance,
            num_prompts=num_prompts,
            starting_prompt_model_id=starting_prompt_model_id,
        )
    )
    assert len(result) > 0, "No prompts generated"
    assert len(result) <= num_prompts, "Generated more prompts than expected"

    for index, row in result.iterrows():
        assert row["prompt_model_id"] is not None, "Prompt-model ID is missing"
        assert (
            row["generation_id"] == "[user_objective_training_data]"
        ), "Incorrect generation_id"
        assert row["prompt_object"] is not None, "Prompt object is missing"
        assert row["prompt_prefix"] is not None, "Prompt prefix is missing"
        assert row["model_object"] is not None, "Model object is missing"


def test_prompt_generation_variants():
    """Test prompt generation of syntactic variants."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    task_request = TaskRequest(
        user_objective="generate a marketing email",
        dataset_file_path="./data/email_gen_demo.csv",
        num_test_data_input=2,
    )

    print("User Objective:", task_request.user_objective)
    print("Input Variables:", task_request.input_variables)

    llm_factory = LLMFactory()

    # Define the OpenAI instance parameters
    openai_params = {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.4,
        "max_tokens": task_request.max_ground_truth_tokens,
    }

    # Create the OpenAI instance
    openai_instance = llm_factory.create_llm(
        openai_params["model_name"], **openai_params
    )

    print("OpenAI instance:", openai_instance)

    # Generate initial prompts using prompt generation user objective method
    num_prompts = 2
    starting_prompt_model_id = 1
    intermediate_result = user_objective.prompt_generation_user_objective(
        task_request=task_request,
        model_object=openai_instance,
        num_prompts=num_prompts,
        starting_prompt_model_id=starting_prompt_model_id,
    )

    # Generate variants of each prompt
    num_variants = 2
    result = variants.prompt_generation_variants(
        task_request=task_request,
        prompt_model_candidates=intermediate_result,
        num_variants=num_variants,
        starting_prompt_model_id=starting_prompt_model_id + num_prompts,
    )

    assert len(result) > 0, "No prompts generated"
    assert (
        len(result) <= num_prompts * num_variants
    ), "Generated more prompts than expected"

    for index, row in result.iterrows():
        assert row["prompt_model_id"] is not None, "Prompt-model ID is missing"
        assert row["generation_id"][-10:] == "_[variant]", "Incorrect generation_id"
        assert row["prompt_object"] is not None, "Prompt object is missing"
        assert row["prompt_prefix"] is not None, "Prompt prefix is missing"
        assert row["model_object"] is not None, "Model object is missing"


def test_prompt_generation_few_shots():
    """Test prompt generation of few-shot based prompts."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    task_request = TaskRequest(
        user_objective="generate a marketing email",
        dataset_file_path="./data/email_gen_demo.csv",
        num_test_data_input=2,
    )

    print("User Objective:", task_request.user_objective)
    print("Input Variables:", task_request.input_variables)

    llm_factory = LLMFactory()

    # Define the OpenAI instance parameters
    openai_params = {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.4,
        "max_tokens": task_request.max_ground_truth_tokens,
    }

    # Create the OpenAI instance
    openai_instance = llm_factory.create_llm(
        openai_params["model_name"], **openai_params
    )

    print("OpenAI instance:", openai_instance)

    # Generate initial prompts using prompt generation user objective method
    num_prompts = 2
    starting_prompt_model_id = 1
    intermediate_result = user_objective.prompt_generation_user_objective(
        task_request=task_request,
        model_object=openai_instance,
        num_prompts=num_prompts,
        starting_prompt_model_id=starting_prompt_model_id,
    )

    # Generate few shot version of each prompt
    result = few_shot.prompt_generation_few_shots(
        task_request=task_request,
        prompt_model_candidates=intermediate_result,
        starting_prompt_model_id=starting_prompt_model_id + num_prompts,
    )

    assert len(result) > 0, "No prompts generated"
    assert len(result) <= num_prompts, "Generated more prompts than expected"

    for index, row in result.iterrows():
        assert row["prompt_model_id"] is not None, "Prompt-model ID is missing"
        assert (
            row["generation_id"][-35:] == "_[few_shots_max_marginal_relevance]"
        ), "Incorrect generation_id"
        assert row["prompt_object"] is not None, "Prompt object is missing"
        assert row["prompt_prefix"] is not None, "Prompt prefix is missing"
        assert row["model_object"] is not None, "Model object is missing"


def test_prompt_generation_temperature_variation():
    """Test prompt generation of temperature variants."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    task_request = TaskRequest(
        user_objective="generate a marketing email",
        dataset_file_path="./data/email_gen_demo.csv",
        num_test_data_input=2,
    )

    print("User Objective:", task_request.user_objective)
    print("Input Variables:", task_request.input_variables)

    llm_factory = LLMFactory()

    # Define the OpenAI instance parameters
    openai_params = {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.4,
        "max_tokens": task_request.max_ground_truth_tokens,
    }

    # Create the OpenAI instance
    openai_instance = llm_factory.create_llm(
        openai_params["model_name"], **openai_params
    )

    print("OpenAI instance:", openai_instance)

    # Generate initial prompts using prompt generation user objective method
    num_prompts = 1
    starting_prompt_model_id = 1
    intermediate_result = user_objective.prompt_generation_user_objective(
        task_request=task_request,
        model_object=openai_instance,
        num_prompts=num_prompts,
        starting_prompt_model_id=starting_prompt_model_id,
    )

    # Generate few shot version of each prompt
    intermediate_few_shot_results = few_shot.prompt_generation_few_shots(
        task_request=task_request,
        prompt_model_candidates=intermediate_result,
        starting_prompt_model_id=starting_prompt_model_id + num_prompts,
    )

    # Generate temperature variant of each few shot prompt
    num_temperature_variants = 3
    result = temperature_variation.prompt_generation_temperature_variation(
        prompt_model_candidates=intermediate_few_shot_results,
        num_prompts=num_temperature_variants,
        starting_prompt_model_id=starting_prompt_model_id + num_prompts * 2,
    )

    assert len(result) > 0, "No prompts generated"
    assert (
        len(result) == num_temperature_variants
    ), "Generated different number of prompts than expected"

    for index, row in result.iterrows():
        assert row["prompt_model_id"] is not None, "Prompt-model ID is missing"
        assert (
            row["generation_id"][-24:] == "_[temperature_variation]"
        ), "Incorrect generation_id"
        assert row["prompt_object"] is not None, "Prompt object is missing"
        assert row["prompt_prefix"] is not None, "Prompt prefix is missing"
        assert row["model_object"] is not None, "Model object is missing"


if __name__ == "__main__":
    pytest.main()
