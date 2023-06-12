"""Defines helper methods for vector databases holding user-provided docs for data repository."""

from app.models.embedding.open_ai import OpenAIEmbeddings
from app.models.vector_stores.pinecone import Pinecone
from app.utilities.dataset_processing import chunk
from config import Config
import pinecone

pinecone.init(api_key=Config.PINECONE_API_KEY, environment=Config.PINECONE_ENVIRONMENT)
pinecone_index = pinecone.Index(Config.PINECONE_INDEX)


VECTOR_DB_NAMESPACE_FORMAT_STRING = "task_id_{task_id}_data_repository"


def initialize_vector_db_data_repository_from_doc(
    task_id: int,
    doc: str,
    openai_api_key: str,
) -> Pinecone:
    # Chunk doc and hold in dataframe
    doc_dataframe = chunk.chunk_doc(text=doc)

    # Setup metadata as list of dicts for each doc chunk
    metadata = doc_dataframe.to_dict(orient="records")

    # Initialize vector db namespace for this task_id
    embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key).embed_query
    namespace = VECTOR_DB_NAMESPACE_FORMAT_STRING.format(task_id=task_id)
    vector_db_data_repository = Pinecone(
        index=pinecone_index,
        embedding_function=embedding_function,
        text_key="text",
        namespace=namespace,
    )
    vector_db_data_repository.add_text_embeddings_and_metadata(
        texts=doc_dataframe["context"].to_list(),
        metadata=metadata,
    )

    return vector_db_data_repository


def load_vector_db_data_repository(
    vector_db_data_repository_metadata: dict,
    openai_api_key: str,
) -> Pinecone:
    """Loads namespace for data repository of this task from vector db.

    Args:
        vector_db_data_repository_metadata (dict): metadata about vector db for data repository of this task.
        openai_api_key (str): OpenAI API key to use for embeddings.

    Returns:
        Pinecone: vector db with selected namespace.
    """
    embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key).embed_query

    vector_db_data_repository = Pinecone(
        index=pinecone_index,
        embedding_function=embedding_function,
        text_key="text",
        namespace=vector_db_data_repository_metadata["namespace"],
    )
    return vector_db_data_repository


def delete_vector_db_data_repository(vector_db_data_repository_metadata: dict) -> None:
    """Deletes namespace for data repository of this task from vector db.

    Args:
        vector_db_data_repository_metadata (dict): metadata about vector db for data repository of this task.
    """
    embedding_function = OpenAIEmbeddings(openai_api_key="NOT_NEEDED").embed_query

    # Delete namespace from vector db
    vector_db_data_repository = Pinecone(
        index=pinecone_index,
        embedding_function=embedding_function,
        text_key="text",
        namespace=vector_db_data_repository_metadata["namespace"],
    )
    vector_db_data_repository.delete_namespace()
