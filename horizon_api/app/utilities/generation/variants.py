"""Generates syntactic variants of the given prompts that are semantically similar to the original."""

from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.component.post_processing.post_processing import PostProcessing
from app.models.example_selector.max_marginal_relevance_example_selector import (
    MaxMarginalRelevanceExampleSelector,
)
from app.utilities.generation import base
from app.utilities.generation import prompt_generation_metaprompts
from app.utilities.generation import prompt_generation_models
from app.utilities.dataset_processing import chunk
from app.models.component.task_request import TaskRequest
from app.models.prompt.factory import PromptTemplateFactory
import json
import copy


def prompt_generation_variants(
    task_request: TaskRequest,
    prompt_model_candidates: PromptModelCandidates,
    num_variants: int,
    starting_prompt_model_id: int,
    openai_api_key: str,
    post_processing: PostProcessing = None,
) -> PromptModelCandidates:
    """Generates syntactic variants of the given prompts that are semantically similar to the original. Assumes prompts are
    PromptTemplate objects.

    Args:
        task_request (TaskRequest): details for this task creation run.
        prompt_model_candidates (PromptModelCandidates): data structure with current set of prompt-model candidates.
        num_variants (int): number of syntatic variants to generate for each existing prompt-model candidate.
        starting_prompt_model_id (int): starting id for new prompt-model candidates.
        openai_api_key (str): OpenAI API key to use.
        post_processing (PostProcessing, optional): details on llm output post-processing operations. Defaults to None.

    Returns:
        PromptModelCandidates: new set of variant prompt-model candidates.
    """
    # Get metaprompts to generate and check new prompt prefixes
    metaprompt_generation = prompt_generation_metaprompts.get_metaprompt_variants()
    metaprompt_check = prompt_generation_metaprompts.get_metaprompt_variants_check()

    # Get llms to generate and check new prompt prefixes
    metaprompt_model_generation = prompt_generation_models.get_model_variants(
        num_prompts=num_variants, openai_api_key=openai_api_key
    )
    metaprompt_model_check = prompt_generation_models.get_model_variants_check(
        openai_api_key=openai_api_key
    )

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

    prompt_model_id_list = []
    generation_id_list = []
    prompt_object_list = []
    prompt_prefix_list = []
    model_object_list = []

    # Iterate through each prompt-model candidate and produce variants of it
    for index, row in prompt_model_candidates.iterrows():
        original_prompt_prefix = row["prompt_prefix"]

        metaprompt_generation_formatted = metaprompt_generation.format(
            original_prompt_prefix=original_prompt_prefix
        )
        responses = metaprompt_model_generation.generate(
            [metaprompt_generation_formatted]
        ).generations[0]

        for i in range(num_variants):
            new_prompt_prefix = responses[i].text.strip()
            prompt_template = (
                new_prompt_prefix + output_format_instructions + prompt_suffix
            )

            # Generate example selector to retrieve context from data repository, if applicable
            context_selector = None
            if task_request.vector_db_data_repository is not None:
                context_selector = MaxMarginalRelevanceExampleSelector(
                    vectorstore=task_request.vector_db_data_repository,
                    k=chunk.NUM_CHUNKS_TO_RETRIEVE_FOR_PROMPT_CONTEXT,
                    example_keys=["context"],
                    input_keys=task_request.input_variables,
                )

            # Check that prompt template has required input variables and is formatted correctly
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

            # Check if new generated prompt is overfitting
            metaprompt_check_formatted = metaprompt_check.format(
                original_prompt_prefix=original_prompt_prefix,
                new_prompt_prefix=new_prompt_prefix,
            )
            overfit_assessment = (
                metaprompt_model_check.generate([metaprompt_check_formatted])
                .generations[0][0]
                .text.strip()
            )
            try:
                overfit_check = json.loads(overfit_assessment)
                assert overfit_check["final_answer"] in ["YES", "NO"]
                if overfit_check["final_answer"] == "YES":
                    continue
            except:
                continue

            # add the generated prompt and new prompt prefix to the prompt_candidates list
            prompt_model_id_list.append(starting_prompt_model_id)
            starting_prompt_model_id += 1
            generation_id_list.append(row["generation_id"] + "_[variant]")
            prompt_object_list.append(generated_prompt)
            prompt_prefix_list.append(new_prompt_prefix)
            model_object_list.append(copy.deepcopy(row["model_object"]))

    # Return new prompt variants
    variant_prompt_model_candidates = PromptModelCandidates(
        prompt_model_id_list=prompt_model_id_list,
        generation_id_list=generation_id_list,
        prompt_object_list=prompt_object_list,
        prompt_prefix_list=prompt_prefix_list,
        model_object_list=model_object_list,
    )
    return variant_prompt_model_candidates
