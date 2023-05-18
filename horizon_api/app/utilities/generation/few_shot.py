"""Generates few-shot based prompts for each of the given prompts."""

from app.models.component.task_request import TaskRequest
from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.embedding.open_ai import OpenAIEmbeddings
from app.models.prompt.factory import PromptTemplateFactory
from app.utilities.generation import base
from app.utilities.generation import prompt_generation_metaprompts
from langchain.vectorstores import FAISS
from langchain.prompts.example_selector import MaxMarginalRelevanceExampleSelector
import copy


def prompt_generation_few_shots(
    task_request: TaskRequest,
    prompt_model_candidates: PromptModelCandidates,
    starting_prompt_model_id: int,
    openai_api_key: str,
) -> PromptModelCandidates:
    """Generates few-shot based prompts for each of the given prompts.

    Args:
        task_request (TaskRequest): details for this task creation run.
        prompt_model_candidates (PromptModelCandidates): data structure with current set of prompt-model candidates.
        starting_prompt_model_id (int): starting id for new prompt-model candidates.

    Returns:
        PromptModelCandidates: new set of few-shot based prompt-model candidates.
    """
    training_dataset = task_request.input_data_train.join(
        task_request.ground_truth_data_train.set_index("evaluation_data_id"),
        on="evaluation_data_id",
    )
    training_dataset = training_dataset.drop("evaluation_data_id", axis=1)
    examples = training_dataset.to_dict("records")
    example_formatter_template = (
        prompt_generation_metaprompts.get_few_shot_example_formatter_template(
            input_variables=task_request.input_variables
        )
    )
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
        few_shot_prompt_prefix = row["prompt_prefix"] + "\n\n==\nEXAMPLES:"
        model_name = row["model_object"].get_model_name()

        # create the example selector
        # examples: This is the list of examples available to select from.
        # embeddings: This is the Embeddings class that is used to embed the examples.
        # vector_store: This is the VectorStore class that is used to store the embeddings and do a similarity search over.
        # k: This is the number of examples to produce.
        example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
            examples,
            OpenAIEmbeddings(openai_api_key=openai_api_key),
            FAISS,
            k=task_request.applicable_llms[model_name]["max_few_shots"],
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
