"""Defines helper methods for vector databases."""

from app.models.embedding.open_ai import OpenAIEmbeddings
from app.models.vector_stores.chroma import Chroma
from app.utilities.dataset_processing import data_check
from app.utilities.dataset_processing import input_variable_naming
from app.utilities.S3.s3_util import download_file_from_s3_and_save_locally
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
import tempfile
import os


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 0
VECTOR_DB_COLLECTION_NAME = "dataset"


def get_vector_db_from_raw_dataset(
    raw_dataset_s3_key: str,
    openai_api_key: str,
    columns_to_chunk: list = None,
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
        evaluation_dataset=raw_dataset
    )

    # Chunk columns if required
    if columns_to_chunk:
        # Ensure that columns_to_chunk are all valid columns in raw_dataset
        assert all(
            column in raw_dataset.columns.to_list() for column in columns_to_chunk
        )

        # Setup text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )

        # Chunk each column
        for column in columns_to_chunk:
            raw_dataset[column] = raw_dataset[column].apply(
                lambda x: text_splitter.split_text(x)
            )
            raw_dataset = raw_dataset.explode(column)
            raw_dataset = raw_dataset.reset_index(drop=True)

    # Setup metadatas as list of dicts for each evaluation data point
    metadatas = raw_dataset.to_dict(orient="records")

    # Setup texts for embedding. Exclude evaluation_data_id so it's not embedded
    texts = [
        "\n\n".join(
            [
                f"{key}: {value}"
                for key, value in record.items()
                if key != "evaluation_data_id"
            ]
        )
        for record in metadatas
    ]

    # Setup vector db
    vector_db_file_path = tempfile.NamedTemporaryFile().name
    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    collection_metadata = {
        "num_unique_data": num_unique_data,
        "input_variables": input_variables,
    }
    vector_db = Chroma(
        collection_name=VECTOR_DB_COLLECTION_NAME,
        embedding_function=embedding,
        persist_directory=vector_db_file_path,
        collection_metadata=collection_metadata,
    )
    vector_db.add_text_embeddings_and_metadatas(texts=texts, metadatas=metadatas)

    return vector_db


def load_vector_db(vector_db_s3_key: str, openai_api_key: str) -> Chroma:
    vector_db_file_path = download_file_from_s3_and_save_locally(vector_db_s3_key)
    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vector_db = Chroma(
        collection_name=VECTOR_DB_COLLECTION_NAME,
        embedding_function=embedding,
        persist_directory=vector_db_file_path,
    )
    return vector_db
