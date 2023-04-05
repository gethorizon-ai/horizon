import pandas as pd


def prompt_shortlist(df, num_of_top_rows_overall, num_of_top_rows_per_metric, metric=None):
    # Check if the metric is in the DataFrame
    if num_of_top_rows_per_metric > 0 and metric not in df.columns:
        return "Error: Metric not found in the DataFrame"

    # Group the DataFrame by prompt_id, generation_id
    df = df.groupby(['prompt_id', 'generation_id']).agg({
        'cosine_similarity_openAI': ['min', 'max', 'mean', ('median', lambda x: x.median())],
        'prompt_object': 'first',
        'prompt_prefix': 'first',
        'model_object': 'first',
    }).reset_index()

    df.columns = ['_'.join(col).strip('_') for col in df.columns.values]
    df = df.rename(columns={'prompt_object_first': 'prompt_object',
                            'prompt_prefix_first': 'prompt_prefix',
                            'model_object_first': 'model_object'})

    # Add score that computes average of min and mean cosine similarity value
    df['min_mean_cosine_similarity'] = (
        df['cosine_similarity_openAI_min'] + df['cosine_similarity_openAI_mean']) / 2

    # Sort the DataFrame by the cosine similarity score in descending order
    sorted_df = df.sort_values('min_mean_cosine_similarity', ascending=False)

    # Get the top n rows with highest score overall
    top_n_overall = sorted_df.head(num_of_top_rows_overall)

    # drop top_n_overall from sorted_df
    sorted_df = sorted_df.drop(top_n_overall.index)

    # Get the top m rows with highest score for each unique metric
    if (metric is not None):
        top_m_per_metric = sorted_df.groupby(metric).apply(
            lambda x: x.nlargest(num_of_top_rows_per_metric, 'min_mean_cosine_similarity'))
        top_m_per_metric = top_m_per_metric.reset_index(
            drop=True)  # reset index to start at 0
    else:
        top_m_per_metric = pd.DataFrame()
    # Combine the two DataFrames and sort by score in descending order
    result_df = pd.concat([top_n_overall, top_m_per_metric]).sort_values(
        'min_mean_cosine_similarity', ascending=False)
    result_df = result_df.reset_index(drop=True)  # reset index to start at 0
    return result_df
