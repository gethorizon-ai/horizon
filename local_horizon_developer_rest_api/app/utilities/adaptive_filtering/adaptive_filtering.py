"""Runs inference, evaluation, and shortlist iterations to efficiently filter down prompt-model candidates."""

from app.models.component.task_request import TaskRequest
from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.component.inference_evaluation_results import InferenceEvaluationResults
from app.utilities.inference import inference
from app.utilities.evaluation import evaluation
from app.utilities.shortlist import shortlist
import numpy as np
import pandas as pd
from typing import Tuple


def adaptive_filtering(
    task_request: TaskRequest,
    prompt_model_candidates: PromptModelCandidates,
    stage_id: str,
    num_shortlist: int,
    num_iterations: int,
) -> Tuple[PromptModelCandidates, InferenceEvaluationResults]:
    """Runs inference, evaluation, and shortlist iterations to efficiently filter down prompt-model candidates.

    Algorithm exponentially reduces prompt-model candidates until it reaches the target number of shortlisted candidates.

    Args:
        task_request (TaskRequest): data structure holding task request information.
        prompt_model_candidates (PromptModelCandidates): data structure with each prompt-model candidate.
        stage_id (str): id for this inference and evaluation stage.
        num_shortlist (int): target number of shortlisted prompt-model candidates.
        num_iterations (int): number of iterations to run adaptive filtering.

    Raises:
        ValueError: checks that provided number of prompt-model candidates exceeds the target shortlist amount.
        ValueError: checks that at least 1 iteration is requested.
        ValueError: checks that there are sufficient test data points to run inputted number of iterations.

    Returns:
        Tuple[PromptModelCandidates, InferenceEvaluationResults]: tuple containing shortlisted set of prompt-model candidates and
            aggregated inference and evaluation results.
    """
    # Check input values
    if num_shortlist >= len(prompt_model_candidates):
        raise ValueError(
            "Target shortlist amount must be less than provided number of prompt-model candidates."
        )
    if num_iterations < 1:
        raise ValueError(
            "Must have at least 1 iteration of inference, evaluation, and shortlisting."
        )
    if num_iterations > task_request.num_test_data:
        raise ValueError(
            "Number of iterations cannot exceed number of test data points."
        )

    # Calculate what % of candidates should be filtered in each iteration to exponentially reduce to target shortlist amount
    filtering_rate = np.power(
        num_shortlist / len(prompt_model_candidates), 1 / num_iterations
    )

    # Determine number of prompt-model candidates in each iteration (i.e., candidate batch size)
    candidate_batch_sizes = [len(prompt_model_candidates)]
    for i in range(1, num_iterations + 1):
        # For final iteration, prompt-model candidates must be reduced to target shortlist amount
        if i == num_iterations:
            candidate_batch_sizes.append(num_shortlist)
        else:
            # Calculate candidate batch size of next iteration by applying the filtering rate
            next_candidate_batch_size = int(
                candidate_batch_sizes[i - 1] * filtering_rate
            )
            # Do not reduce to target shortlist amount if it's not the final iteration
            if next_candidate_batch_size == num_shortlist:
                next_candidate_batch_size = candidate_batch_sizes[i - 1]
            candidate_batch_sizes.append(next_candidate_batch_size)

    # Segment test data points into approximately equal sizes for each iteration
    evaluation_data_id_list = task_request.input_data_test[
        "evaluation_data_id"
    ].to_list()
    evaluation_data_id_segments = np.array_split(
        evaluation_data_id_list, num_iterations
    )
    # Reverse list so that larger segments are in later iterations and convert each element from np array to list
    evaluation_data_id_segments.reverse()
    evaluation_data_id_segments = [
        list(evaluation_data_id_segments[i])
        for i in range(len(evaluation_data_id_segments))
    ]

    # Run inference, evaluation, and shortlist iterations
    shortlisted_prompt_model_candidates = prompt_model_candidates.copy()
    aggregated_inference_evaluation_results = InferenceEvaluationResults()
    for i in range(num_iterations):
        inference_evaluation_results = inference.run_inference(
            task_request=task_request,
            prompt_model_candidates=shortlisted_prompt_model_candidates,
            train_or_test_dataset="test",
            stage_id=stage_id,
            evaluation_data_id_list=evaluation_data_id_segments[i],
        )
        evaluation.run_evaluation(
            task_request=task_request,
            inference_evaluation_results=inference_evaluation_results,
        )

        # Aggregate inference and evaluation results
        aggregated_inference_evaluation_results = pd.concat(
            [aggregated_inference_evaluation_results, inference_evaluation_results],
            axis=0,
        )

        shortlisted_prompt_model_candidates = (
            shortlist.shortlist_prompt_model_candidates(
                prompt_model_candidates=shortlisted_prompt_model_candidates,
                inference_evaluation_results=aggregated_inference_evaluation_results,
                num_shortlist=candidate_batch_sizes[i + 1],
            )
        )

    return (
        shortlisted_prompt_model_candidates,
        aggregated_inference_evaluation_results,
    )
