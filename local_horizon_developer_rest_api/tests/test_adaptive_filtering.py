"""Test adaptive filtering method, which includes inference, evaluation, and shortlist."""

from app.models.llm.factory import LLMFactory
from app.models.component import TaskRequest
from app.utilities.adaptive_filtering import adaptive_filtering
from app.utilities.generation import user_objective
from app.utilities.generation import few_shot
import pytest
from dotenv import load_dotenv
import openai
import os
import pandas as pd


def test_adaptive_filtering():
    """Test adaptive filtering method."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    num_test_data = 6
    task_request = TaskRequest(
        user_objective="generate a marketing email",
        dataset_file_path="./data/email_gen_demo.csv",
        num_test_data_input=num_test_data,
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

    # Generate initial prompts using prompt generation user objective method
    num_prompts = 7
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

    combined_prompt_model_candidates = pd.concat(
        [intermediate_result, intermediate_few_shot_results], axis=0
    )

    # Reduce down to 2 prompts using adaptive filtering over 3 iterations
    num_shortlist = 2
    num_iterations = 3
    (
        shortlisted_prompt_model_candidates,
        aggregated_inference_evaluation_results,
    ) = adaptive_filtering.adaptive_filtering(
        task_request=task_request,
        prompt_model_candidates=combined_prompt_model_candidates,
        stage_id="test_stage",
        num_shortlist=num_shortlist,
        num_iterations=num_iterations,
    )

    assert (
        len(shortlisted_prompt_model_candidates) == num_shortlist
    ), "Shortlisted different number of prompts than expected"


if __name__ == "__main__":
    pytest.main()
