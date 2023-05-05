"""Data structure to track inference and evaluation results during Task creation.

Class stores ids corresponding to prompt-model candidates and evaluation data to avoid duplicating their values, so these
must be fetched from separate data structures when needed.

This class does not optimize for latency associated with DataFrames. This was implemented this way because the primary 
bottleneck is LLM inference, this approach was faster to implement, and it has additional DataFrame functionality that 
may be useful (e.g., as compared to storing values in lists or dicts). This may be optimized later.

Typical usage example:

    inference_evaluation_results = InferenceEvaluationResults(prompt_model_id_list=[x], eval_data_id_list=[x], stage_id='x')
    # iterate over each combination of prompt-model candidate and evaluation datum
    inference_evaluation_results.iloc[i]["output"] = 'x'
"""

import pandas as pd
import numpy as np
from typing import List
from itertools import product


class InferenceEvaluationResults(pd.DataFrame):
    """Wrapper around DataFrame to track inference and evaluation results for prompt-model candidates"""

    def __init__(
        self,
        prompt_model_id_list: List[int] = [],
        evaluation_data_id_list: List[int] = [],
        stage_id: str = "",
    ) -> None:
        """Creates wrapper around DataFrame to track inference and evaluation results for each permutation of
        prompt-model candidate and evaluation datu point provided.

        Args:
            prompt_model_id_list (List[int], optional): list of unique prompt-model candidate ids. Defaults to [].
            evaluation_data_id_list (List[int], optional): list of unique evaluation data ids. Defaults to [].
            stage_id (str, optional): stage id for this inference and evaluation run. Defaults to "".

        Raises:
            ValueError: checks that not only one of prompt_model_id_list or evaluation_data_id_list are empty.
        """
        # Check that not only one of prompt_model_id_list or evaluation_data_id_list are empty
        if (len(prompt_model_id_list) == 0 and len(evaluation_data_id_list) != 0) or (
            len(prompt_model_id_list) != 0 and len(evaluation_data_id_list) == 0
        ):
            raise ValueError(
                "Cannot have only one of prompt_model_id_list or evaluation_data_id_list be empty."
            )
        # If prompt_model_id_list and evaluation_data_id_list are both non-empty, then prepare each permutation of them
        if len(prompt_model_id_list) != 0 and len(evaluation_data_id_list) != 0:
            # Prepare permutations of prompt-model candidates and evaluation data to be computed
            evaluation_permutations = list(
                product(prompt_model_id_list, evaluation_data_id_list)
            )
            unzipped_values = list(zip(*evaluation_permutations))
            prompt_model_id_list = list(unzipped_values[0])
            evaluation_data_id_list = list(unzipped_values[1])

        # Initialize remaining columns in DataFrame
        # Initialize output, inference quality, inference cost, and inference latency with NaN placeholder values
        stage_id = [stage_id] * len(prompt_model_id_list)
        output_list = [np.nan] * len(prompt_model_id_list)
        inference_quality_list = [np.nan] * len(prompt_model_id_list)
        inference_cost_list = [np.nan] * len(prompt_model_id_list)
        inference_latency_list = [np.nan] * len(prompt_model_id_list)
        evaluation_latency_list = [np.nan] * len(prompt_model_id_list)

        # Initialize preallocated DataFrame for inference and evaluation computation
        super().__init__(
            {
                "prompt_model_id": prompt_model_id_list,
                "evaluation_data_id": evaluation_data_id_list,
                "stage_id": stage_id,
                "output": output_list,
                "inference_quality": inference_quality_list,
                "inference_cost": inference_cost_list,
                "inference_latency": inference_latency_list,
                "evaluation_latency": evaluation_latency_list,
            }
        )
