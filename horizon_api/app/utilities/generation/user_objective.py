"""Generates prompt candidates based on user-provided objective and input variables."""

from app.models.prompt.factory import PromptTemplateFactory
from app.models.llm.base import BaseLLM
from app.models.component.task_request import TaskRequest
from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.component.post_processing.post_processing import PostProcessing
from app.models.example_selector.max_marginal_relevance_example_selector import (
    MaxMarginalRelevanceExampleSelector,
)
from app.utilities.generation import base
from app.utilities.generation import prompt_generation_metaprompts
from app.utilities.generation import prompt_generation_models
from app.utilities.dataset_processing import chunk
import copy


def prompt_generation_user_objective(
    task_request: TaskRequest,
    num_prompts: int,
    starting_prompt_model_id: int,
    openai_api_key: str,
    model_object: BaseLLM = None,
    post_processing: PostProcessing = None,
) -> PromptModelCandidates:
    """Generates prompt candidates based on user-provided objective and input variables.

    Args:
        task_request (TaskRequest): details for this task creation run
        num_prompts (int): number of prompt candidates to generate
        starting_prompt_model_id (int): starting id for prompt-model candidates
        openai_api_key (str): OpenAI API key to use.
        model_object (BaseLLM, optional): LLM to use with generated prompt. Defaults to None.
        post_processing (PostProcessing, optional): details on llm output post-processing operations. Defaults to None.

    Returns:
        PromptModelCandidates: data structure with generated prompt-model candidates
    """
    print(f"Starting prompt generation user objective")  # TODO: remove

    # Get metaprompt and format it
    metaprompt = prompt_generation_metaprompts.get_metaprompt_user_objective()

    print(f"Created metaprompt")  # TODO: remove

    formatted_metaprompt = metaprompt.format(
        objective=task_request.user_objective,
        input_variables=base.generate_input_variables_string(
            input_variables=task_request.input_variables
        ),
    )

    print(f"Formatted metaprompt")  # TODO: remove

    # Get LLM
    metaprompt_model = prompt_generation_models.get_model_user_objective(
        num_prompts=num_prompts, openai_api_key=openai_api_key
    )

    print(f"Got LLM")  # TODO: remove

    # Generate prompt candidates
    responses = metaprompt_model.generate([formatted_metaprompt]).generations[0]

    print(f"Generated prompt candidates")  # TODO: remove

    # If post_processing is defined, then append output format instructions to prefix
    output_format_instructions = ""
    if post_processing:
        output_format_instructions = post_processing.output_format_instructions

    prompt_suffix = base.generate_prompt_suffix(
        input_variables=task_request.input_variables,
        include_context_from_data_repository=(
            task_request.vector_db_data_repository is not None
        ),
    )

    context_selector = None
    if task_request.vector_db_data_repository is not None:
        context_selector = MaxMarginalRelevanceExampleSelector(
            vectorstore=task_request.vector_db_data_repository,
            k=chunk.NUM_CHUNKS_TO_RETRIEVE_FOR_PROMPT_CONTEXT,
            example_keys=["context"],
            input_keys=task_request.input_variables,
        )

    print(f"Generated prompt suffix")  # TODO: remove

    prompt_model_id_list = []
    generation_id_list = []
    prompt_object_list = []
    prompt_prefix_list = []
    model_object_list = []
    for i in range(num_prompts):
        # Check that prompt template has required input variables and is formatted correctly
        prompt_prefix = responses[i].text.strip()
        prompt_template = prompt_prefix + output_format_instructions + prompt_suffix

        print(f"Generated prompt template: {prompt_template}")  # TODO: remove

        try:
            generated_prompt = PromptTemplateFactory.create_prompt_template(
                "prompt",
                context_selector=context_selector,
                template=prompt_template,
                input_variables=task_request.input_variables
                + task_request.input_variable_context,
            )
        except:
            continue

        prompt_model_id_list.append(starting_prompt_model_id)
        starting_prompt_model_id += 1
        generation_id_list.append("[user_objective]")
        prompt_object_list.append(generated_prompt)
        prompt_prefix_list.append(prompt_prefix)
        model_object_list.append(copy.deepcopy(model_object))

    prompt_model_candidates = PromptModelCandidates(
        prompt_model_id_list=prompt_model_id_list,
        generation_id_list=generation_id_list,
        prompt_object_list=prompt_object_list,
        prompt_prefix_list=prompt_prefix_list,
        model_object_list=model_object_list,
    )
    return prompt_model_candidates
