"""Computes cosine similarity for each combination of output and ground truth."""

from app.models.component.inference_evaluation_results import InferenceEvaluationResults
from app.models.component.task_request import TaskRequest
from app.models.embedding.open_ai import OpenAIEmbeddings
import time
import numpy as np
import pandas as pd


def get_semantic_cosine_similarity_openAI(
    task_request: TaskRequest,
    inference_evaluation_results: InferenceEvaluationResults,
    openai_api_key: str,
) -> None:
    """Computes cosine similarity for each combination of output and ground truth.

    Inference score and evaluation latency are inserted directly into inference_evaluation_results object.

    Args:
        task_request (TaskRequest): data structure holding task request information such ground truth dataset.
        inference_evaluation_results (InferenceEvaluationResults): data structure with inference results.
        openai_api_key (str): OpenAI API key to use.
    """
    print("Starting evaluation")

    # Get ground truth data corresponding to each evaluation_data_id
    db_results = (
        task_request.vector_db_evaluation_dataset.get_data_per_evaluation_data_id(
            evaluation_data_id_list=inference_evaluation_results["evaluation_data_id"]
            .unique()
            .tolist(),
            include_embeddings=False,
            include_input_variables_in_metadata=False,
        )
    )
    ground_truth_data = pd.DataFrame(db_results["metadata"])

    reference_table = inference_evaluation_results.join(
        ground_truth_data.set_index("evaluation_data_id"),
        on="evaluation_data_id",
    )

    # Compute cosine similarity over every combination of output and ground truth
    for index, row in reference_table.iterrows():
        start_time = time.time()
        if row["output"] != "":
            output_embedding = OpenAIEmbeddings(
                openai_api_key=openai_api_key
            ).embed_query(row["output"])
            ground_truth_embedding = OpenAIEmbeddings(
                openai_api_key=openai_api_key
            ).embed_query(row["ground_truth"])
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

        print(
            f"prompt_model_id: {row['prompt_model_id']} | evaluation_data_id: {row['evaluation_data_id']}"
        )
        print(f"Output: {row['output']}")
        print(f"Ground truth: {row['ground_truth']}")
        print(f"Inference quality: {cosine_similarity}")
