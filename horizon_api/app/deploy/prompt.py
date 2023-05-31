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
from app.utilities.logging.task_logger import TaskLogger
from app.utilities.vector_db import vector_db
from config import Config
from config import Config
import json
from datetime import datetime
import time


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
        # Try to fetch vector db
        if task.evaluation_dataset_vector_db_collection_name:
            evaluation_dataset_vector_db = vector_db.load_vector_db(
                collection_name=task.evaluation_dataset_vector_db_collection_name,
                openai_api_key=Config.HORIZON_OPENAI_API_KEY,
            )

        # If vector db does not exist, set it up from raw evaluation dataset
        elif task.evaluation_dataset:
            evaluation_dataset_vector_db = (
                vector_db.initialize_vector_db_from_raw_dataset(
                    task_id=task_id,
                    raw_dataset_s3_key=task.evaluation_dataset,
                    openai_api_key=Config.HORIZON_OPENAI_API_KEY,
                    input_variables_to_chunk=task.input_variables_to_chunk,
                )
            )

            # Store vector db in task record for future deployments
            evaluation_dataset_vector_db.persist()
            task.evaluation_dataset_vector_db_collection_name = (
                evaluation_dataset_vector_db.get_collection_name()
            )
            db.session.commit()

        # Throw error if no raw or vector db version of evaluation dataset
        else:
            raise ValueError("No vector db or evaluation dataset present")

        prompt_instance = PromptTemplateFactory.reconstruct_prompt_object(
            template_type=template_type,
            evaluation_dataset_vector_db=evaluation_dataset_vector_db,
            template_data=template_data,
        )

    # Prepend "var_" to input variable names as done in Task generation (to prevent collisions with internal variable names)
    processed_input_values = {}
    for variable, value in input_values.items():
        processed_input_values["var_" + variable] = value

    # Format prompt by substituting input values
    original_formatted_prompt = prompt_instance.format(**processed_input_values)

    # If model is ChatOpenAI or ChatAnthropic, wrap message with HumanMessage object
    if type(model_instance) == ChatOpenAI or type(model_instance) == ChatAnthropic:
        formatted_prompt_for_llm = [HumanMessage(content=original_formatted_prompt)]
        prompt_for_data_analysis = formatted_prompt_for_llm
    else:
        formatted_prompt_for_llm = original_formatted_prompt
        prompt_for_data_analysis = [formatted_prompt_for_llm]

    inference_start_time = time.time()

    # Generate output
    llm_result = model_instance.generate([formatted_prompt_for_llm])
    output = llm_result.generations[0][0].text.strip()

    # Conduct post-processing of output, if applicable
    if task.pydantic_model:
        post_processing = PostProcessing(
            pydantic_model_s3_key=task.pydantic_model, llm=model_instance
        )
        output = post_processing.parse_and_retry_if_needed(
            original_output=output, prompt_string=original_formatted_prompt
        )

    inference_end_time = time.time()

    # Release vector db
    del evaluation_dataset_vector_db

    # Log deployment if logging is enabled
    if log_deployment:
        prompt_data_length = model_instance.get_prompt_data_length(
            prompt_messages=prompt_for_data_analysis, llm_result=llm_result
        )
        completion_data_length = model_instance.get_completion_data_length(
            llm_result=llm_result
        )
        prompt_cost = LLMFactory.get_prompt_cost(
            model_name=model_name, prompt_data_length=prompt_data_length
        )
        completion_cost = LLMFactory.get_completion_cost(
            model_name=model_name, completion_data_length=completion_data_length
        )

        logger = TaskLogger()
        logger.log_deployment(
            task_id=prompt.task_id,
            prompt_id=prompt.id,
            timestamp=datetime.utcnow(),
            model_name=model_name,
            input_values=input_values,
            llm_completion=output,
            inference_latency=inference_end_time - inference_start_time,
            data_unit=LLMFactory.get_data_unit(model_name=model_name),
            prompt_data_length=prompt_data_length,
            completion_data_length=completion_data_length,
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            total_inference_cost=prompt_cost + completion_cost,
        )

    return output
