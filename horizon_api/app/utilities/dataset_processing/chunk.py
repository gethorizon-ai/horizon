"""Helper functions to chunk and process evaluation data."""

from app.models.embedding.open_ai import OpenAIEmbeddings
from langchain.text_splitter import NLTKTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz

MIN_CHUNK_LENGTH = 500
MAX_GROUND_TRUTH_LENGTH_MULTIPLIER = 1.5
MAX_NUM_CHUNKS_PER_EVALUATION_DATA_ID = 3


def chunk_and_embed_data(
    user_objective: str,
    evaluation_dataset: pd.DataFrame,
    openai_api_key: str,
    input_variables_to_chunk: List[str] = None,
    task_type: str = None,
) -> dict:
    """Chunks evaluation dataset for the specified input variables and filters chunks to relevant ones.

    Args:
        user_objective (str): user-provided objective statement.
        evaluation_dataset (pd.DataFrame): original unchunked evaluation dataset.
        openai_api_key (str): OpenAI API key to use for embeddings.
        input_variables_to_chunk (List[str], optional): input variables to chunk in evaluation dataset. Defaults to None.
        task_type (str, optional): task type / use case. Defaults to None.

    Returns:
        dict: filtered evaluation dataset, along with embeddings of user objective statement and each data chunk for reuse.
    """
    # If input variables to chunk are specified, then split text for those input variables into chunks
    chunk_length = None
    if input_variables_to_chunk:
        # Ensure that input_variables_to_chunk are all valid input variable names
        assert all(
            (
                var in evaluation_dataset.columns.to_list()
                and var not in ["evaluation_data_id", "ground_truth"]
            )
            for var in input_variables_to_chunk
        )

        # Set chunk length
        max_ground_truth_length = evaluation_dataset["ground_truth"].str.len().max()
        chunk_length = max(
            MIN_CHUNK_LENGTH,
            max_ground_truth_length * MAX_GROUND_TRUTH_LENGTH_MULTIPLIER,
        )

        print(f"Made it just before splitting text")

        # Chunk each input variable, then separate chunks into different rows
        for var in input_variables_to_chunk:
            evaluation_dataset[var] = evaluation_dataset.apply(
                lambda row: split_text(
                    text=row[var],
                    chunk_length=chunk_length,
                    task_type=task_type,
                    ground_truth=row["ground_truth"],
                ),
                axis=1,
            )
            evaluation_dataset = evaluation_dataset.explode(var)
            evaluation_dataset = evaluation_dataset.reset_index(drop=True)

    print(f"Made it just before filtering chunks")

    # Filter chunks to remove potentially irrelevant chunks (i.e., ones without relevant data to generate ground truth) and generate
    # embeddings of user objective and each data point in evaluation dataset
    filtered_evaluation_dataset_and_embeddings = filter_and_embed_chunks(
        user_objective=user_objective,
        evaluation_dataset=evaluation_dataset,
        openai_api_key=openai_api_key,
    )

    # Add chunk length
    filtered_evaluation_dataset_and_embeddings["chunk_length"] = chunk_length

    return filtered_evaluation_dataset_and_embeddings


def split_text(
    text: str,
    chunk_length: int,
    task_type: str = None,
    ground_truth: str = None,
) -> List[str]:
    """Splits text into chunks that satisfy the given chunk length.

    If task type is text extraction, first tries to chunk by extracting substring with best fuzzy match to ground truth.

    If that doesn't work or task type is not text extraction, then first splits text using NLTK text splitter to try to keep as much
    semantic intent / meaning intact. If some of the text splits exceed the given chunk length, then splits further using Recursive
    Character text splitter.

    Assumes no chunk overlap between split texts.

    Args:
        text (str): text to split.
        chunk_length (int): max length of split text.
        task_type (str, optional): task type / use case. Defaults to None.
        ground_truth (str, optional): ground truth for given data point. Defaults to None.

    Returns:
        List[str]: list of split texts.
    """
    if len(text) < chunk_length:
        return [text]

    # If task type is text extraction, try to extract substring with highest fuzzy match similarity score to ground truth
    if task_type == "text_extraction":
        best_match = None
        best_score = 0
        threshold = 95

        for i in range(len(text) - chunk_length + 1):
            substring = text[i : i + chunk_length]
            match_score = fuzz.partial_ratio(substring, ground_truth)

            if match_score > best_score and match_score >= threshold:
                best_match = substring
                best_score = match_score

        if best_match:
            return [best_match]

    # If task type is not text extraction or fuzzy match extraction didn't work, then split text with text splitters
    nltk_text_splitter = NLTKTextSplitter(
        chunk_size=chunk_length,
        chunk_overlap=0,
    )
    recursive_character_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_length,
        chunk_overlap=0,
    )

    # First try NLTK text splitter
    splits = nltk_text_splitter.split_text(text)

    # Check if any of the splits are over chunk lenth (possible with NLTK splitter). If so, split them further
    for i in range(len(splits)):
        if len(splits[i]) > chunk_length:
            # Further split the string with Recursive Character text splitter
            sub_splits = recursive_character_text_splitter.split_text(splits[i])

            # Replace the original string with the first chunk
            splits[i] = sub_splits[0]

            # Insert the remaining chunks after the current string
            splits[i + 1 : i + 1] = sub_splits[1:]

    return splits


def filter_and_embed_chunks(
    user_objective: str,
    evaluation_dataset: pd.DataFrame,
    openai_api_key: str,
    filter_to_top_quartile: bool = True,
) -> dict:
    """Filters chunked evaluation dataset by selecting chunks from each original evaluation data point from the top quartile of
    cosine similarity compared to the user objective.

    Args:
        user_objective (str): user-provided objective statement.
        evaluation_dataset (pd.DataFrame): chunked evaluation dataset.
        openai_api_key (str): OpenAI API key to use for embeddings.

    Returns:
        dict: filtered evaluation dataset, along with embeddings of user objective statement and each data chunk for reuse.
    """
    # Copy evaluation dataset
    evaluation_dataset = evaluation_dataset.copy(deep=True)

    # Setup embedding function
    embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key).embed_query

    # Embed user objective
    user_objective_embedding = embedding_function(user_objective)

    # Create a list of unique evaluation data ids
    evaluation_data_ids = evaluation_dataset["evaluation_data_id"].unique()

    # Add data embeddings as column to evaluation dataset
    # Ground truth value is not incorporated in embedding to prevent overlap with reference embedding column and create
    # apples-to-apples comparison with input values during deployment
    evaluation_dataset["data_embedding"] = evaluation_dataset.apply(
        lambda row: embedding_function(
            "\n".join(
                [
                    f"<{column}>: {row[column]}"
                    for column in evaluation_dataset.columns
                    if column not in ["evaluation_data_id", "ground_truth"]
                ]
            )
        ),
        axis=1,
    )

    # Add embedding of user objective plus ground truth as reference column
    # Iterate across each evaluation data id to avoid duplicate embedding calls over same ground truth values
    for id in evaluation_data_ids:
        # Get ground truth value
        row_ground_truth = evaluation_dataset.loc[
            evaluation_dataset["evaluation_data_id"] == id, "ground_truth"
        ].iloc[0]

        # Calculate reference embedding
        reference_embedding = embedding_function(
            "\n".join([f"{user_objective}\n<OUTPUT>: {row_ground_truth}"])
        )

        # Assign reference embedding to all rows with the same ID
        evaluation_dataset.loc[
            evaluation_dataset["evaluation_data_id"] == id, "reference_embedding"
        ] = reference_embedding

    # Add column that calculates cosine similarity between data and reference embeddings
    evaluation_dataset["cosine_similarity"] = evaluation_dataset.apply(
        lambda row: np.dot(row["data_embedding"], row["reference_embedding"])
        / (
            np.linalg.norm(row["data_embedding"])
            * np.linalg.norm(row["reference_embedding"])
        ),
        axis=1,
    )

    # Filter dataframe by top quartile cosine similarity for each evaluation data id
    filtered_evaluation_dataset = pd.DataFrame()
    for id in evaluation_data_ids:
        filtered_subset = evaluation_dataset[
            evaluation_dataset["evaluation_data_id"] == id
        ]

        # Filter to top quartile if requested
        if filter_to_top_quartile:
            top_quartile_threshold = np.percentile(
                filtered_subset["cosine_similarity"], 75
            )
            filtered_subset = filtered_subset[
                filtered_subset["cosine_similarity"] >= top_quartile_threshold
            ]

        # Ensure that no more than max num of chunks are returned
        if len(filtered_subset) > MAX_NUM_CHUNKS_PER_EVALUATION_DATA_ID:
            filtered_subset = filtered_subset.nlargest(
                MAX_NUM_CHUNKS_PER_EVALUATION_DATA_ID, "cosine_similarity"
            )

        filtered_evaluation_dataset = pd.concat(
            [filtered_evaluation_dataset, filtered_subset]
        )

    # Extract embeddings of filtered dataframe
    filtered_data_embedding = filtered_evaluation_dataset["data_embedding"].to_list()

    # Drop calculation columns from filtered dataframe
    filtered_evaluation_dataset = filtered_evaluation_dataset.drop(
        "data_embedding", axis=1
    )
    filtered_evaluation_dataset = filtered_evaluation_dataset.drop(
        "reference_embedding", axis=1
    )
    filtered_evaluation_dataset = filtered_evaluation_dataset.drop(
        "cosine_similarity", axis=1
    )

    return {
        "user_objective_embedding": user_objective_embedding,
        "data_embedding": filtered_data_embedding,
        "evaluation_dataset": filtered_evaluation_dataset,
    }


def chunk_input_values(
    user_objective: str,
    input_values: dict,
    processed_input_variables_to_chunk: List[str],
    chunk_length: int,
    openai_api_key: str,
) -> dict:
    """Chunks input values.

    Concatenates up to MAX_NUM_CHUNKS_PER_EVALUATION_DATA_ID chunks for input variables that were chunked.

    Args:
        user_objective (str): user objective statement.
        input_values (dict): input values.
        processed_input_variables_to_chunk (List[str]): processed input variables to chunk.
        chunk_length (int): chunk length.
        openai_api_key (str): OpenAI API key to use.

    Returns:
        dict: chunked input values.
    """
    # Convert input values into dataframe
    input_dataset = pd.DataFrame(input_values, index=[0])

    # Chunk each input variable, then separate chunks into different rows
    for var in processed_input_variables_to_chunk:
        input_dataset[var] = input_dataset.apply(
            lambda row: split_text(
                text=row[var],
                chunk_length=chunk_length,
            ),
            axis=1,
        )
        input_dataset = input_dataset.explode(var)
        input_dataset = input_dataset.reset_index(drop=True)

    # Filter to chunks based on cosine similarity to user objective statement
    filtered_dataset_and_embeddings = filter_and_embed_chunks(
        user_objective=user_objective,
        evaluation_dataset=input_dataset,
        openai_api_key=openai_api_key,
        filter_to_top_quartile=False,
    )
    chunked_dataset = filtered_dataset_and_embeddings["evaluation_dataset"]

    # Concatenate chunks for input values that were chunked
    collapsed_dataset = pd.DataFrame()
    for var in chunked_dataset.columns:
        if var in processed_input_variables_to_chunk:
            collapsed_dataset[var] = ["\n".join(chunked_dataset[var].tolist())]
        else:
            collapsed_dataset[var] = [chunked_dataset[var][0]]

    # Return back in dict form
    chunked_and_collapsed_values = collapsed_dataset.to_dict(orient="records")[0]
    return chunked_and_collapsed_values
