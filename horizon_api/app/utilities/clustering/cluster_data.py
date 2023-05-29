"""Embeds input and output data, clusters them into num_clusters, and outputs selected data as list of dicts."""

from app.models.component.task_request import TaskRequest
from app.models.embedding.open_ai import OpenAIEmbeddings
from sklearn.cluster import KMeans
from scipy.spatial.distance import euclidean
import numpy as np
from typing import List


def cluster_shortlist_data(
    task_request: TaskRequest,
    num_clusters: int,
    train_or_test_dataset: str,
) -> List[dict]:
    """Embeds input and output data, clusters them into num_clusters, and returns selected data as list of dicts.

    Args:
        task_request (TaskRequest): data structure holding task request information such input variables and input dataset.
        num_clusters (int): number of clusters to produce and count of data to reduce to.
        train_or_test_dataset (str): indicates which dataset to use; must be either "train" or "test".

    Returns:
        List(dict): list containing a dict representing each selected data point.
    """
    # Pull embeddings and metadatas from vector db
    if train_or_test_dataset == "train":
        db_results = (
            task_request.evaluation_dataset_vector_db.get_data_per_evaluation_data_id(
                evaluation_data_id_list=task_request.train_data_id_list,
                query=task_request.user_objective,
                include_evaluation_data_id_in_metadatas=False,
            )
        )
    elif train_or_test_dataset == "test":
        db_results = (
            task_request.evaluation_dataset_vector_db.get_data_per_evaluation_data_id(
                evaluation_data_id_list=task_request.test_data_id_list,
                query=task_request.user_objective,
                include_evaluation_data_id_in_metadatas=False,
            )
        )
    embeddings = db_results["embeddings"]
    metadatas = db_results["metadatas"]

    # Compute k-means clusters of embeddings
    clusters = KMeans(n_clusters=num_clusters, n_init="auto").fit(embeddings)

    # Loop over all clusters and append metadata corresponding to closest point to the cluster center
    shortlisted_examples = []
    for cluster_index in range(num_clusters):
        # Get all indices of points assigned to this cluster:
        cluster_points_indices = np.where(clusters.labels_ == cluster_index)[0]

        cluster_center = clusters.cluster_centers_[cluster_index]
        min_index = np.argmin(
            [
                euclidean(embeddings[cluster_point_index], cluster_center)
                for cluster_point_index in cluster_points_indices
            ]
        )
        shortlisted_examples.append(metadatas[cluster_points_indices[min_index]])

    return shortlisted_examples
