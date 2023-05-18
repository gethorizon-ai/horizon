"""Provides function to deploy a Prompt object and return the generated output or completion."""

from app import db
from app.models.component.post_processing.post_processing import PostProcessing
from app.models.component.prompt import Prompt
from app.models.component.task import Task
from app.models.llm.factory import LLMFactory
from app.models.llm.open_ai import ChatOpenAI
from app.models.llm.anthropic import ChatAnthropic
from app.models.prompt.factory import PromptTemplateFactory
from app.models.prompt.chat import HumanMessage
from config import Config
import json
from app.utilities.S3.s3_util import download_file_from_s3_and_save_locally
import os
from app.utilities.logging.task_logger import TaskLogger
from datetime import datetime
import time
from app.utilities.cost_calculation import calculate_cost


def deploy_prompt(
    prompt: Prompt,
    input_values: dict,
    openai_api_key: str = None,
    anthropic_api_key: str = None,
    log_deployment: bool = False,
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
    # Get task
    task_id = prompt.task_id
    task = Task.query.get(task_id)

    # Get the model_name from the prompt
    model_name = prompt.model_name

    # Get the model_params from the prompt
    model_params = json.loads(prompt.model)

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

    # Create the model instance
    model_instance = LLMFactory.create_llm(model_name, **model_params)

    # Get the template type from the prompt
    template_type = prompt.template_type

    # Get the template_data from the prompt
    template_data = json.loads(prompt.template_data)

    # Create prompt instance based on if object is zero-shot or few-shot
    if template_type == "prompt":
        prompt_instance = PromptTemplateFactory.reconstruct_prompt_object(
            template_type, **template_data
        )
    elif template_type == "fewshot":
        # If few shot, get evaluation dataset from task
        dataset_s3_key = task.evaluation_dataset

        # Download the dataset from S3 and save it locally
        dataset_file_path = download_file_from_s3_and_save_locally(dataset_s3_key)
        prompt_instance = PromptTemplateFactory.reconstruct_prompt_object(
            template_type=template_type,
            dataset_file_path=dataset_file_path,
            template_data=template_data,
            openai_api_key=Config.HORIZON_OPENAI_API_KEY,
        )

        # Delete the dataset file from the local file system
        os.remove(dataset_file_path)

    # Modify input variables by prepending "var_" as done in Task creation process (to prevent names from matching internal horizonai
    # variable names)
    for input_variable in list(input_values.keys()):
        input_values["var_" + input_variable] = input_values.pop(input_variable)

    # Format the prompt
    original_formatted_prompt = prompt_instance.format(**input_values)
    formatted_prompt_for_llm = original_formatted_prompt

    # If model is ChatOpenAI or ChatAnthropic, then wrap message with HumanMessage object
    if type(model_instance) == ChatOpenAI or type(model_instance) == ChatAnthropic:
        formatted_prompt_for_llm = [HumanMessage(content=formatted_prompt_for_llm)]

    inference_start_time = time.time()

    # Generate the output
    output = (
        model_instance.generate([formatted_prompt_for_llm])
        .generations[0][0]
        .text.strip()
    )

    # Conduct post-processing of output, if applicable
    if task.pydantic_model:
        post_processing = PostProcessing(
            pydantic_model_s3_key=task.pydantic_model, llm=model_instance
        )
        output = post_processing.parse_and_retry_if_needed(
            original_output=output, prompt_string=original_formatted_prompt
        )

    inference_end_time = time.time()

    # Log the deployment if logging is enabled
    if log_deployment:
        logger = TaskLogger()

        prompt_data_length = len(original_formatted_prompt)
        output_data_length = len(output)
        inference_cost = calculate_cost(
            model_name, prompt_data_length, output_data_length
        )

        logger.log_deployment(
            task_id=prompt.task_id,
            prompt_id=prompt.id,
            time_stamp=datetime.utcnow(),
            input_values=input_values,
            llm_output=output,
            inference_latency=inference_end_time - inference_start_time,
            prompt_data_length=prompt_data_length,
            output_data_length=output_data_length,
            model_name=model_name,
            inference_cost=inference_cost,
        )

    return output
