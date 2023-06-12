"""Helper functions to chunk and process data."""

from langchain.text_splitter import NLTKTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
from typing import List

CHUNK_LENGTH = 1000
CHUNK_OVERLAP = 100
NUM_CHUNKS_TO_RETRIEVE_FOR_PROMPT_CONTEXT = 3
MAX_DATA_REPOSITORY_CONTEXT_LENGTH = (
    CHUNK_LENGTH * NUM_CHUNKS_TO_RETRIEVE_FOR_PROMPT_CONTEXT
)


def chunk_doc(text: str) -> pd.DataFrame:
    """Chunk document and return dataframe holding chunks.

    Args:
        text (str): doc text to chunk.

    Returns:
        pd.DataFrame: dataframe with chunked document text.
    """
    # Initialize DataFrame
    doc_dataframe = pd.DataFrame({"context": [text]})

    # Chunk text, then separate chunks into different rows
    doc_dataframe["context"] = doc_dataframe["context"].apply(
        lambda text: split_text(
            text=text,
            chunk_length=CHUNK_LENGTH,
        ),
    )
    doc_dataframe = doc_dataframe.explode("context").reset_index(drop=True)

    return doc_dataframe


def split_text(text: str, chunk_length: int) -> List[str]:
    """Splits text into chunks that satisfy the given chunk length.

    First splits text using NLTK text splitter to try to keep as much semantic intent / meaning intact. If some of the text splits
    exceed the given chunk length, then splits further using Recursive Character text splitter.

    Args:
        text (str): text to split.
        chunk_length (int): max length of split text.

    Returns:
        List[str]: list of split texts.
    """
    if len(text) < chunk_length:
        return [text]

    # Setup text splitters
    nltk_text_splitter = NLTKTextSplitter(
        chunk_size=chunk_length,
        chunk_overlap=CHUNK_OVERLAP,
    )
    recursive_character_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_length,
        chunk_overlap=CHUNK_OVERLAP,
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
