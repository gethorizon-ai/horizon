"""Generates prompt candidates based on user-provided objective, input variables, and training data.

Typical usage example:
    prompt_model_candidates = prompt_generation_user_objective_training_data(experiment=x, model_object=x, num_prompts=x, 
        starting_prompt_model_id=x)

"""

from app.models.prompt.prompt import PromptTemplate
from app.models.llm.base import BaseLLM
from app.models.component.task_request import TaskRequest
from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.utilities.generation import base
from app.utilities.generation import prompt_generation_metaprompts
from app.utilities.generation import prompt_generation_models
import copy


def prompt_generation_user_objective_training_data(
    task_request: TaskRequest,
    model_object: BaseLLM,
    num_prompts: int,
    starting_prompt_model_id: int,
) -> PromptModelCandidates:
    """Generates prompt candidates based on user-provided objective, input variables, and training data.

    Args:
        task_request (TaskRequest): details for this task creation run.
        model_object (BaseLLM): LLM to use with generated prompt.
        num_prompts (int): number of prompt candidates to generate.
        starting_prompt_model_id (int): starting id for prompt-model candidates.

    Returns:
        PromptModelCandidates: data structure with generated prompt-model candidates.
    """
    # Get metaprompt and format it
    few_shot_metaprompt = (
        prompt_generation_metaprompts.get_metaprompt_user_objective_training_data(
            task_request=task_request
        )
    )
    formatted_metaprompt = few_shot_metaprompt.format(
        objective=task_request.user_objective,
        input_variables=base.generate_input_variables_string(
            input_variables=task_request.input_variables
        ),
    )

    # Get LLM
    metaprompt_model = prompt_generation_models.get_model_user_objective_training_data(
        num_prompts=num_prompts
    )

    # Generate prompt candidates
    responses = metaprompt_model.generate([formatted_metaprompt]).generations[0]
    prompt_suffix = base.generate_prompt_suffix(
        input_variables=task_request.input_variables
    )

    prompt_model_id_list = []
    generation_id_list = []
    prompt_object_list = []
    prompt_prefix_list = []
    model_object_list = []
    for i in range(num_prompts):
        # Check that prompt template has required input variables and is formatted correctly
        prompt_prefix = responses[i].text.strip()
        prompt_template = prompt_prefix + prompt_suffix
        try:
            generated_prompt = PromptTemplate(
                template=prompt_template, input_variables=task_request.input_variables
            )
        except:
            continue

        prompt_model_id_list.append(starting_prompt_model_id)
        starting_prompt_model_id += 1
        generation_id_list.append("[user_objective_training_data]")
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
