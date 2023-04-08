"""Data structure to track prompt-model candidates during Task creation.

This class does not optimize for latency since it allows for addition of one row at a time to a DataFrame, which is
known to be slow. This was implemented this way because the primary bottleneck is LLM inference, this approach was faster
to implement, and it has additional DataFrame functionality that may be useful (e.g., as compared to storing values in
lists or dicts). This may be optimized later.

Typical usage example:

    prompt_model_candidates = PromptModelCandidates()
    prompt_model_candidates.add_candidate(prompt_model_id=x, generation_id=x, prompt_prefix=x, prompt_object=x, model_object=x)
"""

import pandas as pd

# from app.models.prompt.base import BasePromptTemplate
# from app.models.llm.base import BaseLLM
from typing import List


class PromptModelCandidates(pd.DataFrame):
    """Wrapper around DataFrame to track prompt-model candidates"""

    def __init__(
        self,
        prompt_model_id_list: List[int] = [],
        generation_id_list: List[str] = [],
        prompt_prefix_list: List[str] = [],
        prompt_object_list: List[str] = [],
        model_object_list: List[str] = [],
    ) -> None:
        """Creates wrapper around DataFrame with given data to organize prompt and model candidates during task creation.

        Args:
            prompt_model_id_list (List[int], optional): list of ids corresponding to each prompt and model candidate. Defaults to [].
            generation_id_list (List[str], optional): list of generation ids. Defaults to [].
            prompt_object_list (List[BasePromptTemplate], optional): list of prompt objects. Defaults to [].
            prompt_prefix_list (List[str], optional): list of prefixes for each prompt object. Defaults to [].
            model_object_list (List[BaseLLM], optional): list of model objects. Defaults to [].
        """
        super().__init__(
            {
                "prompt_model_id": prompt_model_id_list,
                "generation_id": generation_id_list,
                "prompt_prefix": prompt_prefix_list,
                "prompt_object": prompt_object_list,
                "model_object": model_object_list,
            }
        )

    def add_candidate(
        self,
        prompt_model_id: int,
        generation_id: str,
        prompt_prefix: str,
        prompt_object: str,
        model_object: str,
    ) -> None:
        """Add single prompt-model candidate.

        Args:
            prompt_model_id (int): id for prompt-model candidate
            generation_id (str): generation id for prompt-model candidate
            prompt_prefix (str): prompt prefix for prompt-model candidate
            prompt_object (str): prompt object for prompt-model candidate
            model_object (str): model object for prompt-model candidate
        """
        self.loc[len(self.index)] = {
            "prompt_model_id": prompt_model_id,
            "generation_id": generation_id,
            "prompt_prefix": prompt_prefix,
            "prompt_object": prompt_object,
            "model_object": model_object,
        }
