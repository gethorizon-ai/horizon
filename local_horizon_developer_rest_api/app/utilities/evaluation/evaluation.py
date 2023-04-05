from .cosine_similarity import get_semantic_cosine_similarity_openAI


def run_evaluation(df):
    """
    Add evaluation score metrics to dataframe
    """
    # Add cosine similarity scores
    get_semantic_cosine_similarity_openAI(df)
    # df_with_scores['avg_score'] = df_with_scores[[
    #     'cosine_similarity_openAI']].mean(axis=1)
