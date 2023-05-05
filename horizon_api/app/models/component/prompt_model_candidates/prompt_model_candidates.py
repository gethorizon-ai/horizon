"""Data structure to track prompt-model candidates during Task creation.

This class does not optimize for latency since it allows for addition of one row at a time to a DataFrame, which is
known to be slow. This was implemented this way because the primary bottleneck is LLM inference, this approach was faster
to implement, and it has additional DataFrame functionality that may be useful (e.g., as compared to storing values in
lists or dicts). This may be optimized later.

Typical usage example:

    prompt_model_candidates = PromptModelCandidates()
    prompt_model_candidates.add_candidate(prompt_model_id=x, generation_id=x, prompt_prefix=x, prompt_object=x, model_object=x)
"""

from app.models.llm.base import BaseLLM
from app.models.prompt.base import BasePromptTemplate
import pandas as pd
import copy

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
        prompt_object_list: List[BasePromptTemplate] = [],
        model_object_list: List[BaseLLM] = [],
    ) -> None:
        """Creates wrapper around DataFrame with given data to organize prompt and model candidates during task creation.

        Args:
            prompt_model_id_list (List[int], optional): list of ids corresponding to each prompt and model candidate. Defaults to [].
            generation_id_list (List[str], optional): list of generation ids. Defaults to [].
            prompt_prefix_list (List[str], optional): list of prefixes for each prompt object. Defaults to [].
            prompt_object_list (List[BasePromptTemplate], optional): list of prompt objects. Defaults to [].
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
