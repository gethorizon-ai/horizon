"""Provides function to deploy a Prompt object and return the generated output or completion."""

from app.models.component.prompt import Prompt
from app.models.component.task import Task
from app import db
from app.models.llm.factory import LLMFactory
from app.models.llm.open_ai import ChatOpenAI
from app.models.llm.anthropic import ChatAnthropic
from app.models.prompt.factory import PromptTemplateFactory
from app.models.prompt.chat import HumanMessage
from config import Config
import json


def deploy_prompt(
    prompt: Prompt,
    input_values: dict,
    openai_api_key: str = None,
    anthropic_api_key: str = None,
) -> str:
    """Deploy a prompt with the given prompt_id and input_values.

    Args:
        prompt (Prompt): prompt object from db.
        input_values (dict): dict of key-value pairs representing the input variables for prompt.
        openai_api_key (str): OpenAI API key to use if selected model is from OpenAI. Defaults to None.
        anthropic_api_key (str, optional): Anthropic API key to use if selected model is from Anthropic. Defaults to None.

    Raises:
        ValueError: if selected model is from OpenAI, then need to provide OpenAI API key.
        ValueError: if selected model is from Anthropic, then need to provide Anthropic API key.

    Returns:
        str: The output or completion of the deployed prompt.
    """
    # get the model_name from the prompt
    print("HELLO TO YOU!!!")
    model_name = prompt.model_name

    # get the model_params from the prompt
    print("HI TO YOU!!!")
    model_params = json.loads(prompt.model)
    print(f"Model params: {model_params}")

    # Add llm api key
    if LLMFactory.llm_classes[model_name]["provider"] == "OpenAI":
        if openai_api_key == None:
            raise ValueError("Need OpenAI API key since selected LLM is from OpenAI.")
        model_params["openai_api_key"] = openai_api_key
    elif LLMFactory.llm_classes[model_name]["provider"] == "Anthropic":
        if anthropic_api_key == None:
            raise ValueError(
                "Need Anthropic API key since selected LLM is from Anthropic."
            )
        model_params["anthropic_api_key"] = anthropic_api_key

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
    print(f"Template data: {template_data}")

    # Create prompt instance based on if object is zero-shot or few-shot
    if template_type == "prompt":
        prompt_instance = prompt_factory.reconstruct_prompt_object(
            template_type, **template_data
        )
    elif template_type == "fewshot":
        # If few shot, get evaluation dataset from task
        # Reconstruct few shot example selector with embeddings using Horizon's OpenAI API key
        task_id = prompt.task_id
        task = Task.query.get(task_id)
        dataset_file_path = task.evaluation_dataset
        prompt_instance = prompt_factory.reconstruct_prompt_object(
            template_type=template_type,
            dataset_file_path=dataset_file_path,
            template_data=template_data,
            openai_api_key=Config.HORIZON_OPENAI_API_KEY,
        )

    # Modify input variables by prepending "var_" as done in Task creation process (to prevent names from matching internal horizonai
    # variable names)
    for input_variable in list(input_values.keys()):
        input_values["var_" + input_variable] = input_values.pop(input_variable)

    # format the prompt
    formatted_prompt = prompt_instance.format(**input_values)

    print(f"Formatted prompt: {formatted_prompt}")
    print(f"Model instance: {type(model_instance)}")

    # If model is ChatOpenAI or ChatAnthropic, then wrap message with HumanMessage object
    if type(model_instance) == ChatOpenAI or type(model_instance) == ChatAnthropic:
        formatted_prompt = [HumanMessage(content=formatted_prompt)]

    # generate the output
    output = model_instance.generate([formatted_prompt]).generations[0][0].text.strip()

    # return the output
    return output
