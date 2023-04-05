from app.models.prompt.factory import PromptTemplateFactory as factory
from app.models.prompt.prompt import PromptTemplate
from app.models.prompt.base import BasePromptTemplate
from app.models.schema import HumanMessage
from app.models.llm.factory import LLMFactory
from app.models.component.experiment import Experiment
import pandas as pd
import copy
import json
from app.utilities.generation.user_objective import prompt_generation_user_objective
from app.utilities.generation.pattern_roleplay import prompt_generation_pattern_roleplay
import csv
import os
from dotenv import load_dotenv
import openai
from app.models.component.prompt import Prompt
from app.models.component.task import Task
from app.models.component.project import Project
from app.utilities.inference.inference import run_inference
from app.utilities.evaluation.evaluation import run_evaluation
from app.utilities.shortlist.shortlist import prompt_shortlist
from app import db


def generate_prompt(objective, prompt_id) -> BasePromptTemplate:

    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Get the prompt from the database using the prompt_id
    prompt = Prompt.query.get(prompt_id)
    if not prompt:
        raise ValueError("Prompt not found")

    # Get the task and project associated with the prompt
    task_id = prompt.task_id
    task = Task.query.get(task_id)
    project_id = task.project_id
    project = Project.query.get(project_id)

    # Get the evaluation dataset from the project. If there is no evaluation dataset, return an error
    if not project.evaluation_datasets:
        return {"error": "No evaluation_datasets file associated with this project"}, 404

    # Fetch the evaluation dataset from the project
    with open(project.evaluation_datasets, 'r', encoding='utf-8') as evaluation_datasets_file:
        reader = csv.DictReader(evaluation_datasets_file)

        # Convert the evaluation dataset to a pandas dataframe
        curr_evaluation_dataset = pd.DataFrame([row for row in reader])

    # Create the experiment data dictionary to pass to the Experiment class constructor method
    experiment_data = {
        'user_objective': objective,
        # get the input variables from the evaluation dataset columns and remove the last column which is the ground truth column
        'input_variables': curr_evaluation_dataset.columns[:-1].tolist(),

        'evaluation_dataset': curr_evaluation_dataset,
        'input_values_test': [
            curr_evaluation_dataset.iloc[0:10, 0].reset_index(
                drop=True),
            curr_evaluation_dataset.iloc[0:10, 1].reset_index(
                drop=True),
            curr_evaluation_dataset.iloc[0:10, 2].reset_index(
                drop=True),
            curr_evaluation_dataset.iloc[0:10, 3].reset_index(
                drop=True),
            curr_evaluation_dataset.iloc[0:10, 4].reset_index(
                drop=True),
        ],
        'ground_truth_test': curr_evaluation_dataset.iloc[0:10, 5].reset_index(drop=True),
        'input_values_train': [
            curr_evaluation_dataset.iloc[0:15, 0].reset_index(
                drop=True),
            curr_evaluation_dataset.iloc[0:15, 1].reset_index(
                drop=True),
            curr_evaluation_dataset.iloc[0:15, 2].reset_index(
                drop=True),
            curr_evaluation_dataset.iloc[0:15, 3].reset_index(
                drop=True),
            curr_evaluation_dataset.iloc[0:15, 4].reset_index(
                drop=True),
        ],
        'ground_truth_train': curr_evaluation_dataset.iloc[0:15, 5].reset_index(drop=True)
    }

    # Create the Experiment instance
    experiment_instance = Experiment.from_dict(experiment_data)
    print("Experiment instance created", experiment_instance, "\n")

    # define the LLM factory instance
    llm_factory = LLMFactory()

    # define the models to use
    # Define the OpenAI instance parameters
    openai_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.7,
    }

    # Create the OpenAI instance
    openai_instance = llm_factory.create_llm("openai", **openai_params)

    # save the model to the database
    prompt.model_name = "openai"
    prompt.model = json.dumps(openai_params)

    # Define the global prompt ID
    global_prompt_id = [0]
    prompt_template_type = "prompt"

    # Generate the prompts using the pattern roleplay method
    num_prompt = 1
    prompts_pattern_role_play = prompt_generation_pattern_roleplay(
        experiment_instance, openai_instance, num_prompt, global_prompt_id, prompt_template_type)

    # Generate the prompts using the user objective method
    num_prompt = 1
    prompts_user_objective = prompt_generation_user_objective(
        experiment_instance, openai_instance, num_prompt, global_prompt_id, prompt_template_type)

    # combine the prompts from the two methods
    prompts_generated = prompts_pattern_role_play.append(
        prompts_user_objective)

    # run the prompts through the inference engine
    inference_results = run_inference(
        experiment_instance, prompts_generated, "test")

    # run the infrence results through the evaluation engine
    run_evaluation(inference_results)

    # put the evaluation results through a shortlist engine
    winning_prompt = prompt_shortlist(inference_results, 1, 0)

    # store the winning prompt template type in the database

    prompt.template_type = prompt_template_type

    # store the winning prompt in the database using the prompt_id as the template parameter
    prompt.template_data = json.dumps(winning_prompt["prompt_object"].iloc[0])

    # save the prompt to the database

    # commit the changes to the database
    db.session.commit()

    # return the winning prompt
    return winning_prompt["prompt_object"].iloc[0]


if __name__ == "__main__":
    generate_prompt()
