"""Test inference method."""

from app.models.llm.factory import LLMFactory
from app.models.component import TaskRequest
from app.utilities.generation import user_objective
from app.utilities.inference import inference
import pytest
import dotenv
import os
import numpy as np


def test_inference():
    """Test inference method."""
    dotenv.load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    num_test_data = 2
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
        "openai_api_key": openai_api_key,
    }

    # Create the OpenAI instance
    openai_instance = llm_factory.create_llm(
        openai_params["model_name"], **openai_params
    )

    # Generate prompts using prompt generation user objective method
    num_prompts = 3
    starting_prompt_model_id = 1
    prompt_model_candidates = user_objective.prompt_generation_user_objective(
        task_request=task_request,
        model_object=openai_instance,
        num_prompts=num_prompts,
        starting_prompt_model_id=starting_prompt_model_id,
        openai_api_key=openai_api_key,
    )

    # Run inference
    inference_evaluation_results = inference.run_inference(
        task_request=task_request,
        prompt_model_candidates=prompt_model_candidates,
        train_or_test_dataset="test",
        stage_id=f"[test_inference]",
    )

    # Check that inference results are populated
    assert len(inference_evaluation_results) == num_prompts * num_test_data
    for index, row in inference_evaluation_results.iterrows():
        assert row["output"] != np.NaN
        assert row["inference_latency"] != np.NaN


if __name__ == "__main__":
    pytest.main()
