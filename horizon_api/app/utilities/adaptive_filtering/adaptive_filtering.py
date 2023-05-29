"""Runs inference, evaluation, and shortlist iterations to efficiently filter down prompt-model candidates."""

from app.models.component.task_request import TaskRequest
from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.component.inference_evaluation_results import InferenceEvaluationResults
from app.models.component.post_processing.post_processing import PostProcessing
from app.utilities.inference import inference
from app.utilities.evaluation import evaluation
from app.utilities.shortlist import shortlist
import numpy as np
import pandas as pd
from typing import Tuple, List


def adaptive_filtering(
    task_request: TaskRequest,
    prompt_model_candidates: PromptModelCandidates,
    stage_id: str,
    num_shortlist: int,
    num_iterations: int,
    openai_api_key: str,
    post_processing: PostProcessing = None,
) -> Tuple[PromptModelCandidates, InferenceEvaluationResults]:
    """Runs inference, evaluation, and shortlist iterations to efficiently filter down prompt-model candidates.

    Algorithm exponentially reduces prompt-model candidates until it reaches the target number of shortlisted candidates.

    Args:
        task_request (TaskRequest): data structure holding task request information.
        prompt_model_candidates (PromptModelCandidates): data structure with each prompt-model candidate.
        stage_id (str): id for this inference and evaluation stage.
        num_shortlist (int): target number of shortlisted prompt-model candidates.
        num_iterations (int): number of iterations to run adaptive filtering.
        openai_api_key (str): OpenAI API key to use.
        post_processing (PostProcessing, optional): details on llm output post-processing operations. Defaults to None.

    Raises:
        ValueError: checks that provided number of prompt-model candidates exceeds the target shortlist amount.
        ValueError: checks that at least 1 iteration is requested.
        ValueError: checks that there are sufficient test data points to run inputted number of iterations.

    Returns:
        Tuple[PromptModelCandidates, InferenceEvaluationResults]: tuple containing shortlisted set of prompt-model candidates and
            aggregated inference and evaluation results.
    """
    # Check input values
    if num_shortlist > len(prompt_model_candidates):
        raise ValueError(
            "Target shortlist amount cannot be greater than provided number of prompt-model candidates."
        )
    if num_iterations < 1:
        raise ValueError(
            "Must have at least 1 iteration of inference, evaluation, and shortlisting."
        )
    if num_iterations > task_request.num_test_data:
        raise ValueError(
            "Number of iterations cannot exceed number of test data points."
        )

    # Determine number of prompt-model candidates in each iteration (i.e., candidate batch size)
    candidate_batch_sizes = get_num_prompt_model_candidates_per_iteration(
        num_original_prompt_model_candidates=len(prompt_model_candidates),
        num_shortlist=num_shortlist,
        num_iterations=num_iterations,
    )
    print(f"Candidate batch sizes: {candidate_batch_sizes}")

    # Segment test data points into approximately equal sizes for each iteration
    evaluation_data_id_list = task_request.test_data_id_list
    evaluation_data_id_segments = np.array_split(
        evaluation_data_id_list, num_iterations
    )

    # Reverse list so that larger segments are in later iterations and convert each element from np array to list
    evaluation_data_id_segments.reverse()
    evaluation_data_id_segments = [
        list(evaluation_data_id_segments[i])
        for i in range(len(evaluation_data_id_segments))
    ]
    print(f"Evalution data id list: {evaluation_data_id_segments}")

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
            post_processing=post_processing,
        )
        print("Finished inference")
        evaluation.run_evaluation(
            task_request=task_request,
            inference_evaluation_results=inference_evaluation_results,
            openai_api_key=openai_api_key,
        )
        print("Finished evaluation")

        # Aggregate inference and evaluation results
        aggregated_inference_evaluation_results = pd.concat(
            [aggregated_inference_evaluation_results, inference_evaluation_results],
            axis=0,
        ).reset_index(drop=True)

        shortlisted_prompt_model_candidates = (
            shortlist.shortlist_prompt_model_candidates(
                prompt_model_candidates=shortlisted_prompt_model_candidates,
                inference_evaluation_results=aggregated_inference_evaluation_results,
                num_shortlist=candidate_batch_sizes[i + 1],
            )
        )
        print(
            f"Number of shortlisted candidates: {len(shortlisted_prompt_model_candidates)}"
        )

    return (
        shortlisted_prompt_model_candidates,
        aggregated_inference_evaluation_results,
    )


def get_num_prompt_model_candidates_per_iteration(
    num_original_prompt_model_candidates: int,
    num_shortlist: int,
    num_iterations: int,
) -> List[int]:
    """Get number of prompt-model candidates available in each iteration of adaptive filtering.

    Starts by listing original number of prompt-model candidates and then lists number of available prompt-model candidates after
    every iteration.

    Args:
        num_original_prompt_model_candidates (int): number of original prompt-model candidates at start of adaptive filtering.
        num_shortlist (int): numbef of prompt-model candidates to shortlist to at end of adaptive filtering.
        num_iterations (int): number of iterations of adaptive filtering algorithm.

    Returns:
        List[int]: number of prompt-model candidates at each iteration, including the original number at the start.
    """
    # Calculate what % of candidates should be filtered in each iteration to exponentially reduce to target shortlist amount
    filtering_rate = np.power(
        num_shortlist / num_original_prompt_model_candidates, 1 / num_iterations
    )

    # Determine number of prompt-model candidates in each iteration (i.e., candidate batch size)
    candidate_batch_sizes = [num_original_prompt_model_candidates]
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

    return candidate_batch_sizes


def get_num_data_per_iteration(num_data: int, num_iterations: int) -> List[int]:
    """Get number of data points used for inference and evaluation in each iteration of adaptive filtering.

    Args:
        num_data (int): total number of data points to be used across adaptive filtering algorithm.
        num_iterations (int): number of iterations of adaptive filtering algorithm.

    Returns:
        List[int]: number of data points used for inference and evaluation in each iteration of adaptive filtering.
    """
    # Simulate segmentation of data points into approximately equal sizes for each iteration
    evaluation_data_id_list = list(range(num_data))
    evaluation_data_id_segments = np.array_split(
        evaluation_data_id_list, num_iterations
    )

    # Reverse list so that larger segments are in later iterations
    evaluation_data_id_segments.reverse()

    # Count number of data points in each iteration
    num_data_per_iteration = [len(x) for x in evaluation_data_id_segments]

    return num_data_per_iteration


def get_total_num_inferences(
    num_original_prompt_model_candidates: int,
    num_data: int,
    num_shortlist: int,
    num_iterations: int,
) -> int:
    """Calculate total number of llm inferences made during adaptive filtering run.

    Args:
        num_original_prompt_model_candidates (int): number of original prompt-model candidates at start of adaptive filtering.
        num_data (int): total number of data points to be used across adaptive filtering algorithm.
        num_shortlist (int): numbef of prompt-model candidates to shortlist to at end of adaptive filtering.
        num_iterations (int): number of iterations of adaptive filtering algorithm.

    Returns:
        int: total number of llm inferences made during adaptive filtering run.
    """
    # Get number of prompt-model candidates in each iteration (i.e., candidate batch size)
    candidate_batch_sizes = get_num_prompt_model_candidates_per_iteration(
        num_original_prompt_model_candidates=num_original_prompt_model_candidates,
        num_shortlist=num_shortlist,
        num_iterations=num_iterations,
    )

    # Exclude final shortlisted number of prompt-model candidates (since all inferences are completed by then)
    candidate_batch_sizes = candidate_batch_sizes[:-1]

    # Get number of data points used for inference and evaluation in each iteration
    num_data_per_iteration = get_num_data_per_iteration(
        num_data=num_data, num_iterations=num_iterations
    )

    # Calculate total number of inferences across adaptive filtering run
    return np.dot(candidate_batch_sizes, num_data_per_iteration)
