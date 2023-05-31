"""Defines helper methods for vector databases."""

from app.models.embedding.open_ai import OpenAIEmbeddings
from app.models.vector_stores.pinecone import Pinecone
from app.utilities.dataset_processing import input_variable_naming
from config import Config
import pandas as pd
import pinecone

pinecone.init(api_key=Config.PINECONE_API_KEY, environment=Config.PINECONE_ENVIRONMENT)
pinecone_index = pinecone.Index(Config.PINECONE_INDEX)


VECTOR_DB_NAMESPACE_FORMAT_STRING = "task_id_{task_id}"


def initialize_vector_db_from_dataset(
    task_id: int,
    evaluation_dataset: pd.DataFrame,
    openai_api_key: str,
) -> Pinecone:
    """Initializes entries into vector db from raw evaluation dataset.

    Args:
        task_id (int): id of task.
        evaluation_dataset (pd.DataFrame): dataframe holding evaluation dataset.
        openai_api_key (str): OpenAI API key to use for embeddings.
        input_variables_to_chunk (list, optional): list of input variable names for which to chunk values. Defaults to None.

    Returns:
        Pinecone: _description_
    """

    num_unique_data = len(evaluation_dataset)
    input_variables = input_variable_naming.get_input_variables(
        dataset_fields=evaluation_dataset.columns.to_list()
    )

    # Setup metadata as list of dicts for each evaluation data point
    metadata = evaluation_dataset.to_dict(orient="records")

    # Setup texts for embedding. Exclude evaluation_data_id so it's not embedded
    # TODO: exclude ground_truth from embedding?
    texts = [
        "\n".join(
            [
                f"<{key}>: {value}"
                for key, value in record.items()
                if key != "evaluation_data_id"
            ]
        )
        for record in metadata
    ]

    # Initialize vector db namespace for this task_id
    embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key).embed_query
    namespace = VECTOR_DB_NAMESPACE_FORMAT_STRING.format(task_id=task_id)
    vector_db = Pinecone(
        index=pinecone_index,
        embedding_function=embedding_function,
        text_key="text",
        namespace=namespace,
        input_variables=input_variables,
        num_unique_data=num_unique_data,
    )
    vector_db.add_text_embeddings_and_metadata(texts=texts, metadata=metadata)

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
        namespace=vector_db_metadata["namespace"],
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
