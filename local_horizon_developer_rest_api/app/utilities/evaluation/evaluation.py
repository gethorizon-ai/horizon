"""Evaluates inference for each combination of output and ground truth."""

from . import cosine_similarity
from app.models.component.inference_evaluation_results import InferenceEvaluationResults
from app.models.component.task_request import TaskRequest


def run_evaluation(
    task_request: TaskRequest,
    inference_evaluation_results: InferenceEvaluationResults,
    openai_api_key: str,
) -> None:
    """Evaluates inference for each combination of output and ground truth.

    Inference score and evaluation latency are inserted directly into inference_evaluation_results object.

    Args:
        task_request (TaskRequest): data structure holding task request information such ground truth dataset.
        inference_evaluation_results (InferenceEvaluationResults): data structure with inference results.
    """
    # Get cosine similarity scores
    cosine_similarity.get_semantic_cosine_similarity_openAI(
        task_request=task_request,
        inference_evaluation_results=inference_evaluation_results,
        openai_api_key=openai_api_key,
    )
