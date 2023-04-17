"""Embeds input and output data, clusters them into num_clusters, and outputs selected data as list of dicts."""

from app.models.component.task_request import TaskRequest
from langchain.embeddings import OpenAIEmbeddings
from sklearn.cluster import KMeans
from scipy.spatial.distance import euclidean
import numpy as np
from typing import List


def cluster_shortlist_data(
    task_request: TaskRequest, num_clusters: int, train_or_test_dataset: str
) -> List[dict]:
    """Embeds input and output data, clusters them into num_clusters, and outputs selected data as list of dicts.

    Args:
        task_request (TaskRequest): data structure holding task request information such input variables and input dataset.
        num_clusters (int): number of clusters to produce and count of data to reduce to.
        train_or_test_dataset (str): indicates which dataset to use; must be either "train" or "test".

    Returns:
        List(dict): list containing a dict representing each selected data point.
    """
    # Select input and ground truth data from train or test dataset
    if train_or_test_dataset == "train":
        input_data = task_request.input_data_train
        ground_truth_data = task_request.ground_truth_data_train
    elif train_or_test_dataset == "test":
        input_data = task_request.input_data_test
        ground_truth_data = task_request.ground_truth_data_test

    # Join input and ground truth data, and drop evaluation_data_id
    combined_data = input_data.join(
        ground_truth_data.set_index("evaluation_data_id"), on="evaluation_data_id"
    )
    combined_data = combined_data.drop("evaluation_data_id", axis=1)

    # Function to calculate embedding of each example
    def calculate_embedding(example: dict) -> float:
        example_string = ""
        for key, value in example.items():
            example_string += f"<{key}>: {value}\n"
        example_string = example_string.strip()
        return OpenAIEmbeddings().embed_query(example_string)

    # Calculate embedding of each example data
    example_embeddings = combined_data.apply(
        lambda row: calculate_embedding(row.to_dict()), axis=1
    ).to_list()

    # Compute k-means clusters of embeddings
    clusters = KMeans(n_clusters=num_clusters, n_init="auto").fit(example_embeddings)

    # Loop over all clusters and find index of closest point to the cluster center and append to closest_prompt_index list
    closest_prompt_index = []
    for cluster_index in range(num_clusters):
        # Get all indices of points assigned to this cluster:
        cluster_points_indices = np.where(clusters.labels_ == cluster_index)[0]

        cluster_center = clusters.cluster_centers_[cluster_index]
        min_index = np.argmin(
            [
                euclidean(example_embeddings[cluster_point_index], cluster_center)
                for cluster_point_index in cluster_points_indices
            ]
        )
        closest_prompt_index.append(cluster_points_indices[min_index])

    # Shortlist examples to those closest to the centroid of each cluster and return as list of dicts
    shortlisted_examples = combined_data.loc[closest_prompt_index].to_dict("records")
    return shortlisted_examples
