from langchain.embeddings import OpenAIEmbeddings
from sklearn.cluster import KMeans
from scipy.spatial.distance import euclidean


def cluster_shortlist_data(experiment: dict, num_clusters: int, train_or_test: str) -> list:
    """
    Embeds input and output data and returns num_clusters of them as list of dicts
    """
    # Select input and ground truth data from train or test dataset
    if train_or_test == 'train':
        input_values = experiment['input_values_train']
        ground_truth = experiment['ground_truth_train']
    elif train_or_test == 'test':
        input_values = experiment['input_values_test']
        ground_truth = experiment['ground_truth_test']

    # Build list of dictionaries for example data
    examples = []
    for i in range(len(ground_truth)):
        example = {}
        for j in range(len(experiment['input_variables'])):
            example[experiment['input_variables'][j]
                    ] = input_values[j].iloc[i]
        example['output'] = ground_truth.iloc[i]
        examples.append(example)

    # Function to calculate embedding of each example
    def calculate_embedding(example: dict) -> float:
        example_string = ''
        for key, value in example.items():
            example_string += '<{key}>: {value}\n'.format(key=key, value=value)
        example_string = example_string.strip()
        return OpenAIEmbeddings().embed_query(example_string)

    # Embed examples and compute k-means clusters of them
    example_embeddings = [calculate_embedding(example) for example in examples]
    clusters = KMeans(n_clusters=num_clusters).fit(example_embeddings)

    # Loop over all clusters and find index of closest point to the cluster center and append to closest_prompt_index list
    closest_prompt_index = []
    for cluster_index in range(num_clusters):
        # Get all indices of points assigned to this cluster:
        cluster_points_indices = np.where(clusters.labels_ == cluster_index)[0]

        cluster_center = clusters.cluster_centers_[cluster_index]
        min_index = np.argmin([euclidean(example_embeddings[cluster_point_index],
                              cluster_center) for cluster_point_index in cluster_points_indices])
        closest_prompt_index.append(cluster_points_indices[min_index])

    # Shortlist examples to those closest to the centroid of each cluster
    shortlisted_examples = [examples[index] for index in closest_prompt_index]
    return shortlisted_examples
