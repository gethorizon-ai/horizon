"""Defines helper methods for vector databases."""

from app.models.embedding.open_ai import OpenAIEmbeddings
from app.models.vector_stores.chroma import Chroma
from app.utilities.dataset_processing import data_check
from app.utilities.dataset_processing import input_variable_naming
from app.utilities.S3.s3_util import download_file_from_s3_and_save_locally
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
import os


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 0
VECTOR_DB_PERSIST_DIRECTORY = ".chromadb/"
VECTOR_DB_COLLECTION_NAME_FORMAT_STRING = "task_id_{task_id}"


def initialize_vector_db_from_raw_dataset(
    task_id: int,
    raw_dataset_s3_key: str,
    openai_api_key: str,
    input_variables_to_chunk: list = None,
) -> Chroma:
    # Get raw dataset
    raw_dataset_file_path = download_file_from_s3_and_save_locally(raw_dataset_s3_key)
    raw_dataset = data_check.get_evaluation_dataset(
        dataset_file_path=raw_dataset_file_path,
        escape_curly_braces=True,
    )
    os.remove(raw_dataset_file_path)
    num_unique_data = len(raw_dataset)
    input_variables = input_variable_naming.get_input_variables(
        dataset_fields=raw_dataset.columns.to_list()
    )

    # Chunk input variables if required
    if input_variables_to_chunk:
        # Ensure that input_variables_to_chunk are all valid columns in raw_dataset
        assert all(
            var in raw_dataset.columns.to_list() for var in input_variables_to_chunk
        )

        # Setup text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )

        # Chunk each input variable
        for var in input_variables_to_chunk:
            raw_dataset[var] = raw_dataset[var].apply(
                lambda x: text_splitter.split_text(x)
            )
            raw_dataset = raw_dataset.explode(var)
            raw_dataset = raw_dataset.reset_index(drop=True)

    # Setup metadatas as list of dicts for each evaluation data point
    metadatas = raw_dataset.to_dict(orient="records")

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
        for record in metadatas
    ]

    # Initialize vector db collection for this task_id
    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    collection_metadata = {
        "task_id": task_id,
        "num_unique_data": num_unique_data,
        "input_variables": input_variables,
    }
    vector_db = Chroma(
        collection_name=VECTOR_DB_COLLECTION_NAME_FORMAT_STRING.format(task_id=task_id),
        embedding_function=embedding,
        persist_directory=VECTOR_DB_PERSIST_DIRECTORY,
        collection_metadata=collection_metadata,
    )
    vector_db.add_text_embeddings_and_metadatas(texts=texts, metadatas=metadatas)

    return vector_db


def load_vector_db(
    collection_name: str,
    openai_api_key: str,
) -> Chroma:
    """Loads collection from vector db corresponding to given task_id.

    Args:
        collection_name (str): name of vector db collection.
        openai_api_key (str): OpenAI API key to use for embeddings.

    Returns:
        Chroma: vector db with selected collection.
    """
    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vector_db = Chroma(
        collection_name=collection_name,
        embedding_function=embedding,
        persist_directory=VECTOR_DB_PERSIST_DIRECTORY,
    )

    # Check that collection previously existed by testing if it already has items
    # If not, delete newly created collection and throw error
    if vector_db._collection.count() == 0:
        vector_db.delete_collection()
        raise ValueError(
            "Collection did not previously exist for this task id (since there were no pre-existing items)"
        )

    return vector_db


def delete_vector_db_collection(collection_name: str) -> None:
    """Deletes given collection from vector db.

    Args:
        collection_name (str): name of collection to delete.
    """
    vector_db = Chroma(
        collection_name=collection_name,
        persist_directory=VECTOR_DB_PERSIST_DIRECTORY,
    )
    vector_db.delete_collection()
