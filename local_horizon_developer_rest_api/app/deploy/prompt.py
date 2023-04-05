from app.models.component.prompt import Prompt
import os
from dotenv import load_dotenv
import openai
from app import db
from app.models.llm.factory import LLMFactory
from app.models.prompt.factory import PromptTemplateFactory
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
    openai.api_key = os.getenv('OPENAI_API_KEY')

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

    # get the template_data from the prompt
    template_data = json.loads(prompt.template_data)

    # define the prompt factory instance
    prompt_factory = PromptTemplateFactory()

    # Create the prompt instance
    prompt_instance = prompt_factory.create_prompt_template(
        template_type, **template_data)

    # format the prompt
    formated_prompt = prompt_instance.format(**input_values)

    # generate the output
    output = model_instance.generate(
        [formated_prompt]).generations[0][0].text.strip()

    # return the output
    return output
