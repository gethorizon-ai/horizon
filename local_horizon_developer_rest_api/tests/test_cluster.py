"""Test methods to cluster and shortlist items (e.g., cluster shortlist prompts)."""

from app.models.llm.factory import LLMFactory
from app.models.component import TaskRequest
from app.utilities.generation import user_objective
from app.utilities.inference import inference
from app.utilities.evaluation import evaluation
from app.utilities.clustering import cluster_data
from app.utilities.clustering import cluster_prompts
import pytest
from dotenv import load_dotenv
import openai
import os
import numpy as np


def test_cluster_shortlist_data():
    """Test method to cluster and shortlist data from train or test evaluation datasets."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    num_test_data = 8
    task_request = TaskRequest(
        user_objective="generate a marketing email",
        dataset_file_name="./data/email_gen_demo.csv",
        num_test_data=num_test_data,
    )

    print("User Objective:", task_request.user_objective)
    print("Input Variables:", task_request.input_variables)

    # Shortlist test dataset
    num_clusters = 4
    shortlisted_data = cluster_data.cluster_shortlist_data(
        task_request=task_request,
        num_clusters=num_clusters,
        train_or_test_dataset="test",
    )

    # Check output
    assert len(shortlisted_data) == num_clusters


def test_cluster_shortlist_prompts():
    """Test method to cluster and shortlist prompt-model candidates based on prompt prefixes."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create the TaskRequest instance
    num_test_data = 2
    task_request = TaskRequest(
        user_objective="generate a marketing email",
        dataset_file_name="./data/email_gen_demo.csv",
        num_test_data=num_test_data,
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

    # Generate prompts using prompt generation user objective method
    num_prompts = 10
    starting_prompt_model_id = 1
    prompt_model_candidates = user_objective.prompt_generation_user_objective(
        task_request=task_request,
        model_object=openai_instance,
        num_prompts=num_prompts,
        starting_prompt_model_id=starting_prompt_model_id,
    )

    # Shortlist prompt-model candidates
    num_clusters = 5
    shortlisted_prompt_model_candidates = cluster_prompts.cluster_shortlist_prompts(
        prompt_model_candidates=prompt_model_candidates, num_clusters=num_clusters
    )

    # Check output
    assert len(shortlisted_prompt_model_candidates) == num_clusters


if __name__ == "__main__":
    pytest.main()
