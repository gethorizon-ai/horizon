"""Shortlists given prompt-model candidates by clustering prompt prefixes and picking prompt prefix closest to cluster centroids."""

from app.models.component.prompt_model_candidates import PromptModelCandidates
from langchain.embeddings import OpenAIEmbeddings
from sklearn.cluster import KMeans
from scipy.spatial.distance import euclidean
import numpy as np


def cluster_shortlist_prompts(
    prompt_model_candidates: PromptModelCandidates,
    num_clusters: int,
    openai_api_key: str,
) -> PromptModelCandidates:
    """Shortlists given prompt-model candidates by clustering prompt prefixes and picking prompt prefix closest to cluster centroids.

    Args:
        prompt_model_candidates (PromptModelCandidates): data structure with each prompt-model candidate.
        num_clusters (int): number of clusters to produce and count of prompt-model candidates to reduce to.
        openai_api_key (str): OpenAI API key to use.

    Raises:
        ValueError: checks that number of clusters cannot exceed original count of prompt-model candidates.

    Returns:
        PromptModelCandidates: shortlisted set of prompt-model candidates.
    """
    if num_clusters > len(prompt_model_candidates):
        raise ValueError(
            "Number of clusters to shortlist to cannot exceed number of prompts."
        )
    # Calculate embedding of each prompt prefix
    prompt_prefix_embeddings = prompt_model_candidates.apply(
        lambda row: OpenAIEmbeddings(openai_api_key=openai_api_key).embed_query(
            row["prompt_prefix"]
        ),
        axis=1,
    ).to_list()

    # Compute k-means clusters of prompt templates
    clusters = KMeans(n_clusters=num_clusters, n_init="auto").fit(
        prompt_prefix_embeddings
    )

    # Loop over all clusters and find index of closest point to the cluster center and append to
    # closest_prompt_index list
    closest_prompt_index = []
    for cluster_index in range(num_clusters):
        # Get all indices of points assigned to this cluster:
        cluster_points_indices = np.where(clusters.labels_ == cluster_index)[0]

        cluster_center = clusters.cluster_centers_[cluster_index]
        min_index = np.argmin(
            [
                euclidean(prompt_prefix_embeddings[cluster_point_index], cluster_center)
                for cluster_point_index in cluster_points_indices
            ]
        )
        closest_prompt_index.append(cluster_points_indices[min_index])

    # Shortlist prompt-model candidates to those closest to the centroid of each cluster
    shortlisted_prompt_model_candidates = prompt_model_candidates.iloc[
        closest_prompt_index
    ].reset_index(drop=True)
    return shortlisted_prompt_model_candidates
