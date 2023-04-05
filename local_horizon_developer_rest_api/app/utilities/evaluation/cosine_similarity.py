import time
import numpy as np
from langchain.embeddings import OpenAIEmbeddings
import copy


import numpy as np
import pandas as pd
import time


def get_semantic_cosine_similarity_openAI(df):
    # Initialize the columns with NaN
    df['cosine_similarity_openAI'] = np.nan
    df['latency_openAI'] = np.nan

    for i, row in df.iterrows():
        start_time = time.time()
        if row['output'] != '':
            completion_embedding = OpenAIEmbeddings(
            ).embed_query(str(row['output']))
            highlight_embedding = OpenAIEmbeddings(
            ).embed_query(str(row['ground_truth']))
            cosine_similarity = np.dot(completion_embedding, highlight_embedding) / (
                np.linalg.norm(completion_embedding) * np.linalg.norm(highlight_embedding))
        else:
            cosine_similarity = 0
        end_time = time.time()
        latency = end_time - start_time
        df['cosine_similarity_openAI'].iloc[i] = cosine_similarity
        df['latency_openAI'].iloc[i] = latency
