"""Defines helper methods for vector databases."""

from app.models.embedding.open_ai import OpenAIEmbeddings
from app.models.vector_stores.pinecone import Pinecone
from app.utilities.dataset_processing import input_variable_naming
from config import Config
import pandas as pd
import pinecone
from typing import List

pinecone.init(api_key=Config.PINECONE_API_KEY, environment=Config.PINECONE_ENVIRONMENT)
pinecone_index = pinecone.Index(Config.PINECONE_INDEX)


VECTOR_DB_DATA_NAMESPACE_FORMAT_STRING = "task_id_{task_id}_data"


def initialize_vector_db_from_dataset(
    task_id: int,
    data_embedding: List[List[float]],
    evaluation_dataset: pd.DataFrame,
    openai_api_key: str,
) -> Pinecone:
    """Initializes entries into vector db from evaluation dataset.

    Option to provide pre-computed embeddings for each row of evaluation dataset. If not provided, calculates embeddings for each row.

    Args:
        task_id (int): id of task.
        data_embedding (List[List[float]], optional): pre-computed embeddings for each row of evaluation dataset. Defaults to None.
        evaluation_dataset (pd.DataFrame): dataframe holding evaluation dataset.
        openai_api_key (str): OpenAI API key to use for embeddings.

    Returns:
        Pinecone: initialized vector db.
    """
    num_unique_data = len(evaluation_dataset["evaluation_data_id"].unique().tolist())
    input_variables = input_variable_naming.get_input_variables(
        dataset_fields=evaluation_dataset.columns.to_list()
    )

    # Initialize vector db namespace for this task_id
    embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key).embed_query
    data_namespace = VECTOR_DB_DATA_NAMESPACE_FORMAT_STRING.format(task_id=task_id)
    vector_db = Pinecone(
        index=pinecone_index,
        embedding_function=embedding_function,
        text_key="text",
        namespace=data_namespace,
        input_variables=input_variables,
        num_unique_data=num_unique_data,
    )

    # Setup metadata as list of dicts for each evaluation data point
    metadata = evaluation_dataset.to_dict(orient="records")

    vector_db.add_text_embeddings_and_metadata(
        metadata=metadata,
        data_embedding=data_embedding,
    )

    return vector_db


def load_vector_db(
    vector_db_metadata: dict,
    openai_api_key: str,
) -> Pinecone:
    """Loads namespace for the task from vector db.

    Args:
        vector_db_metadata (dict): metadata about vector db usage for this task.
        openai_api_key (str): OpenAI API key to use for embeddings.

    Returns:
        Pinecone: vector db with selected namespace.
    """
    embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key).embed_query

    vector_db = Pinecone(
        index=pinecone_index,
        embedding_function=embedding_function,
        text_key="text",
        namespace=vector_db_metadata["data_namespace"],
        input_variables=vector_db_metadata["input_variables"],
        num_unique_data=vector_db_metadata["num_unique_data"],
    )
    return vector_db


def delete_vector_db(vector_db_metadata: dict) -> None:
    """Deletes namespace for this task from vector db.

    Args:
        vector_db_metadata (dict): metadata about vector db usage for this task.
    """
    embedding_function = OpenAIEmbeddings(openai_api_key="NOT_NEEDED").embed_query

    # Delete namespace from vector db
    vector_db = Pinecone(
        index=pinecone_index,
        embedding_function=embedding_function,
        text_key="text",
        namespace=vector_db_metadata["namespace"],
    )
    vector_db.delete_namespace()
