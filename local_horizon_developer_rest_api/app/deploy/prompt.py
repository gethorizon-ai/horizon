from app.models.component.prompt import Prompt
from app.models.component.task import Task
from app import db
from app.models.llm.factory import LLMFactory
from app.models.llm.open_ai import ChatOpenAI
from app.models.llm.anthropic import Anthropic
from app.models.prompt.factory import PromptTemplateFactory
from app.models.prompt.chat import HumanMessage
import json


def deploy_prompt(
    prompt: Prompt,
    input_values: dict,
    openai_api_key: str,
    anthropic_api_key: str = None,
) -> str:
    """Deploy a prompt with the given prompt_id and input_values.

    Args:
        prompt (Prompt): prompt object from db.
        input_values (dict): dict of key-value pairs representing the input variables for prompt.
        openai_api_key (str): OpenAI API key to use.
        anthropic_api_key (str, optional): Anthropic API key to use if selected model is from Anthropic. Defaults to None.

    Raises:
        ValueError: if selected model is from Anthropic, then need to provide Anthropic API key

    Returns:
        str: The return value of the deployed prompt.

    Args:
        prompt (Prompt): _description_
        input_values (dict): _description_
        openai_api_key (str): _description_
        anthropic_api_key (str, optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        str: _description_
    """
    # get the model_name from the prompt
    model_name = prompt.model_name

    # get the model_params from the prompt
    model_params = json.loads(prompt.model)

    # Add llm api key
    if LLMFactory.llm_classes[model_name]["provider"] == "OpenAI":
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
            openai_api_key=openai_api_key,
        )

    # Modify input variables by prepending "var_" as done in Task creation process (to prevent names from matching internal horizonai
    # variable names)
    for input_variable in list(input_values.keys()):
        input_values["var_" + input_variable] = input_values.pop(input_variable)

    # format the prompt
    formatted_prompt = prompt_instance.format(**input_values)

    # If model is ChatOpenAI, then wrap message with HumanMessage object
    if type(model_instance) == ChatOpenAI:
        formatted_prompt = [HumanMessage(content=formatted_prompt)]
    # If model is Anthropic, then wrap message with Human and AI prompts
    elif type(model_instance) == Anthropic:
        formatted_prompt = f"{model_instance.HUMAN_PROMPT} {formatted_prompt}{model_instance.AI_PROMPT}"

    # generate the output
    output = model_instance.generate([formatted_prompt]).generations[0][0].text.strip()

    # return the output
    return output
