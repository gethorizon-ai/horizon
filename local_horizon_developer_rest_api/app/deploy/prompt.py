from app.models.component.prompt import Prompt
from app.models.component.task import Task
import os
from dotenv import load_dotenv
import openai
from app import db
from app.models.llm.factory import LLMFactory
from app.models.prompt.factory import PromptTemplateFactory
from app.models.prompt.chat import HumanMessage
import json


def deploy_prompt(prompt_id, input_values):
    """
    Deploy a prompt with the given prompt_id and input_values.

    Args:
        prompt_id (int): The ID of the prompt to deploy.
        input_values (dict): A dictionary of key-value pairs representing the input variables for the prompt.

    Returns:
        str: The return value of the deployed prompt.
    """

    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Get the prompt from the database using the prompt_id
    prompt = Prompt.query.get(prompt_id)
    if not prompt:
        raise ValueError("Prompt not found")

    # get the model_name from the prompt
    model_name = prompt.model_name

    # get the model_params from the prompt
    model_params = json.loads(prompt.model)

    # define the LLM factory instance
    llm_factory = LLMFactory()

    # Create the model instance
    model_instance = llm_factory.create_llm(model_name, **model_params)

    # get the template type from the prompt
    template_type = prompt.template_type

    # define the prompt factory instance
    prompt_factory = PromptTemplateFactory()

    # get the template_data from the prompt
    template_data = json.loads(prompt.template_data)

    # Create prompt instance based on if object is zero-shot or few-shot
    if template_type == "prompt":
        prompt_instance = prompt_factory.reconstruct_prompt_object(
            template_type, **template_data
        )
    elif template_type == "fewshot":
        # If few shot, get evaluation dataset from task and few shot example selector data
        task_id = prompt.task_id
        task = Task.query.get(task_id)
        dataset_file_path = task.evaluation_dataset
        prompt_instance = prompt_factory.reconstruct_prompt_object(
            template_type=template_type,
            dataset_file_path=dataset_file_path,
            template_data=template_data,
        )

    # Modify input variables by prepending "var_" as done in Task creation process (to prevent names from matching internal horizonai
    # variable names)
    for input_variable in list(input_values.keys()):
        input_values["var_" + input_variable] = input_values.pop(input_variable)

    # format the prompt
    formatted_prompt = prompt_instance.format(**input_values)

    # If model is ChatOpenAI, then wrap message around a HumanMessage object
    if model_name == "gpt-3.5-turbo":
        formatted_prompt = [HumanMessage(content=formatted_prompt)]

    # generate the output
    output = model_instance.generate([formatted_prompt]).generations[0][0].text.strip()

    # return the output
    return output
