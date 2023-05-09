"""Generate prompt-model candidates that vary model temperature of provided prompt-model candidates."""

from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.llm.open_ai import OpenAI, ChatOpenAI
from app.models.llm.anthropic import ChatAnthropic
import numpy as np
import copy


def prompt_generation_temperature_variation(
    prompt_model_candidates: PromptModelCandidates,
    num_prompts: int,
    starting_prompt_model_id: int,
) -> PromptModelCandidates:
    """For each of the given prompt candidates, generate new prompt candidates with same prompt but varying model temperatures.

    Args:
        prompt_model_candidates (PromptModelCandidates): data structure with current set of prompt-model candidates.
        num_prompts (int): number of prompt candidates to generate.
        starting_prompt_model_id (int): starting id for new prompt-model candidates.

    Returns:
        PromptModelCandidates: new set of prompt-model candidates with varying temperatures.
    """
    # Try uniformly distributed temperature options between 0.1-0.9
    temperature_trials = np.linspace(0.1, 0.9, num_prompts)

    prompt_model_id_list = []
    generation_id_list = []
    prompt_object_list = []
    prompt_prefix_list = []
    model_object_list = []

    # Iterate through each prompt-model candidate and generate a version for each temperature option
    for index, row in prompt_model_candidates.iterrows():
        for temperature in temperature_trials:
            prompt_model_id_list.append(starting_prompt_model_id)
            starting_prompt_model_id += 1
            generation_id_list.append(row["generation_id"] + "_[temperature_variation]")
            prompt_object_list.append(copy.deepcopy(row["prompt_object"]))
            prompt_prefix_list.append(copy.deepcopy(row["prompt_prefix"]))

            selected_model = row["model_object"]
            new_model = copy.deepcopy(selected_model)
            new_model.set_temperature(temperature=temperature)
            model_object_list.append(new_model)

    # Return new prompts with temperature variations
    temperature_variants_prompt_model_candidates = PromptModelCandidates(
        prompt_model_id_list=prompt_model_id_list,
        generation_id_list=generation_id_list,
        prompt_object_list=prompt_object_list,
        prompt_prefix_list=prompt_prefix_list,
        model_object_list=model_object_list,
    )
    return temperature_variants_prompt_model_candidates
