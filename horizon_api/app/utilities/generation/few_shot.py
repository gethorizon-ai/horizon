"""Generates few-shot based prompts for each of the given prompts."""

from app.models.component.task_request import TaskRequest
from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.component.post_processing.post_processing import PostProcessing
from app.models.prompt.factory import PromptTemplateFactory
from app.models.example_selector.max_marginal_relevance_example_selector import (
    MaxMarginalRelevanceExampleSelector,
)
from app.utilities.generation import base
from app.utilities.generation import prompt_generation_metaprompts
import copy


def prompt_generation_few_shots(
    task_request: TaskRequest,
    prompt_model_candidates: PromptModelCandidates,
    starting_prompt_model_id: int,
    post_processing: PostProcessing = None,
) -> PromptModelCandidates:
    """Generates few-shot based prompts for each of the given prompts.

    Args:
        task_request (TaskRequest): details for this task creation run.
        prompt_model_candidates (PromptModelCandidates): data structure with current set of prompt-model candidates.
        starting_prompt_model_id (int): starting id for new prompt-model candidates.
        post_processing (PostProcessing, optional): details on llm output post-processing operations. Defaults to None.

    Returns:
        PromptModelCandidates: new set of few-shot based prompt-model candidates.
    """
    # Get template for each few shot example
    example_formatter_template = (
        prompt_generation_metaprompts.get_few_shot_example_formatter_template(
            input_variables=task_request.input_variables
        )
    )

    # If post_processing is defined, then append output format instructions to prefix
    output_format_instructions = ""
    if post_processing:
        output_format_instructions = post_processing.output_format_instructions

    suffix_request = base.generate_prompt_suffix(
        input_variables=task_request.input_variables
    ).strip()

    prompt_model_id_list = []
    generation_id_list = []
    prompt_object_list = []
    prompt_prefix_list = []
    model_object_list = []

    # Iterate through each prompt-model candidate and produce a few shot version of it
    for index, row in prompt_model_candidates.iterrows():
        few_shot_prompt_prefix = (
            row["prompt_prefix"] + output_format_instructions + "\n\n==\nEXAMPLES:"
        )
        model_name = row["model_object"].get_model_name()

        print(
            f"k used for few-shot: {task_request.applicable_llms[model_name]['max_few_shots']}"
        )
        example_selector = MaxMarginalRelevanceExampleSelector(
            vectorstore=task_request.evaluation_dataset_vector_db,
            k=task_request.applicable_llms[model_name]["max_few_shots"],
            example_keys=task_request.input_variables + ["ground_truth"],
            filter_statement={
                "evaluation_data_id": {"$lt": task_request.num_train_data}
            },
        )

        # create the few shot prompt template
        few_shot_prompt = PromptTemplateFactory.create_prompt_template(
            "fewshot",
            example_selector=example_selector,
            example_prompt=example_formatter_template,
            prefix=few_shot_prompt_prefix,
            suffix=suffix_request,
            input_variables=task_request.input_variables,
        )

        # add the few shot prompt to the prompt_candidates list
        prompt_model_id_list.append(starting_prompt_model_id)
        starting_prompt_model_id += 1
        generation_id_list.append(
            row["generation_id"] + "_[few_shots_max_marginal_relevance]"
        )
        prompt_object_list.append(few_shot_prompt)
        prompt_prefix_list.append(row["prompt_prefix"])
        model_object_list.append(copy.deepcopy(row["model_object"]))

    # Return new few shot prompts
    few_shot_prompt_model_candidates = PromptModelCandidates(
        prompt_model_id_list=prompt_model_id_list,
        generation_id_list=generation_id_list,
        prompt_object_list=prompt_object_list,
        prompt_prefix_list=prompt_prefix_list,
        model_object_list=model_object_list,
    )
    return few_shot_prompt_model_candidates
