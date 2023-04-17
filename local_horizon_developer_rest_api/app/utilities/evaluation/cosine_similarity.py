"""Computes cosine similarity for each combination of output and ground truth."""

from app.models.component.inference_evaluation_results import InferenceEvaluationResults
from app.models.component.task_request import TaskRequest
from langchain.embeddings import OpenAIEmbeddings
import time
import numpy as np


def get_semantic_cosine_similarity_openAI(
    task_request: TaskRequest, inference_evaluation_results: InferenceEvaluationResults
) -> None:
    """Computes cosine similarity for each combination of output and ground truth.

    Inference score and evaluation latency are inserted directly into inference_evaluation_results object.

    Args:
        task_request (TaskRequest): data structure holding task request information such ground truth dataset.
        inference_evaluation_results (InferenceEvaluationResults): data structure with inference results.
    """
    # Get ground truth data corresponding to each evaluation_data_id
    reference_table = inference_evaluation_results.join(
        task_request.evaluation_dataset[
            ["evaluation_data_id", "ground_truth"]
        ].set_index("evaluation_data_id"),
        on="evaluation_data_id",
    )

    # Compute cosine similarity over every combination of output and ground truth
    for index, row in reference_table.iterrows():
        start_time = time.time()
        if row["output"] != "":
            output_embedding = OpenAIEmbeddings().embed_query(row["output"])
            ground_truth_embedding = OpenAIEmbeddings().embed_query(row["ground_truth"])
            cosine_similarity = np.dot(output_embedding, ground_truth_embedding) / (
                np.linalg.norm(output_embedding)
                * np.linalg.norm(ground_truth_embedding)
            )
        else:
            cosine_similarity = 0
        end_time = time.time()
        evaluation_latency = end_time - start_time

        # Record inference quality and evaluation latency in inference_evaluation_results object
        inference_evaluation_results.loc[index, "inference_quality"] = cosine_similarity
        inference_evaluation_results.loc[
            index, "evaluation_latency"
        ] = evaluation_latency
