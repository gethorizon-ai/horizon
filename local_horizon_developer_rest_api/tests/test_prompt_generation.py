from app.models.prompt.factory import PromptTemplateFactory as factory
from app.models.prompt.prompt import PromptTemplate
from app.models.schema import HumanMessage
from app.models.llm.factory import LLMFactory
from app.models.component.experiment import Experiment
import pandas as pd
import copy
import json
import pytest
from app.utilities.generation.user_objective import prompt_generation_user_objective
from app.utilities.generation.pattern_roleplay import prompt_generation_pattern_roleplay
import os
from dotenv import load_dotenv
import openai


def test_user_objective():
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Define the input data
    experiment_data = {
        "user_objective": "generate a marketing email",
        "input_variables": ["context"]
    }

    # Create the Experiment instance
    experiment_instance = Experiment.from_dict(experiment_data)

    print("User Objective:", experiment_instance.user_objective)
    print("Input Variables:", experiment_instance.input_variables)

    llm_factory = LLMFactory()

    # Define the OpenAI instance parameters
    openai_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.4,
        "max_tokens": 1000,
        "n": 1,
        "best_of": 1
    }

    # Create the OpenAI instance
    openai_instance = llm_factory.create_llm("openai", **openai_params)

    print("OpenAI instance:", openai_instance)

    num_prompt = 1
    global_id = [0]
    result = prompt_generation_pattern_roleplay(
        experiment_instance, openai_instance, num_prompt, global_id)
    assert len(result) > 0, "No prompts generated"
    assert len(result) <= num_prompt, "Generated more prompts than expected"

    for index, row in result.iterrows():
        assert row['prompt_id'] is not None, "Prompt ID is missing"
        # assert row['generation_id'] == '[user_objective]', "Incorrect generation_id"
        assert row['prompt_object'] is not None, "Prompt object is missing"
        assert row['prompt_prefix'] is not None, "Prompt prefix is missing"
        assert row['model_object'] is not None, "Model object is missing"


if __name__ == "__main__":
    pytest.main()
