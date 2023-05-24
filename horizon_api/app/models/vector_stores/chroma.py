"""Wrapper around LangChain Chroma object."""

from .base import BaseVectorStore
from langchain.vectorstores import Chroma as ChromaOriginal
from typing import Any, Iterable, List, Optional, Dict
import uuid
import pandas as pd


class Chroma(BaseVectorStore, ChromaOriginal):
    def add_text_embeddings_and_metadatas(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Embed texts and add associated ids, embeddings, and metadatas to vectorstore without adding texts themselves.

        Not adding texts reduces memory required. This is useful when all the data in the text is captured in the metadatas.

        Args:
            texts (Iterable[str]): Texts to add to the vectorstore.
            metadatas (Optional[List[dict]], optional): Optional list of metadatas.
            ids (Optional[List[str]], optional): Optional list of IDs.

        Returns:
            List[str]: List of IDs of the added texts.
        """
        if ids is None:
            ids = [str(uuid.uuid1()) for _ in texts]
        embeddings = None
        if self._embedding_function is not None:
            embeddings = self._embedding_function.embed_documents(list(texts))
        self._collection.add(metadatas=metadatas, embeddings=embeddings, ids=ids)
        return ids

    def get_num_unique_data_from_collection_metadata(self) -> int:
        """Returns number of unique data points (i.e., rows in evaluation dataset before chunking) from collection metadata assuming
        it was added there upon creation of collection.

        Returns:
            int: number of unique data points.
        """
        return self._collection.metadata["num_unique_data"]

    def get_input_variables_from_collection_metadata(self) -> list:
        """Returns list of input variables from collection metadata assuming it was added there upon creation of collection.

        Returns:
            list: list of input variables.
        """
        return self._collection.metadata["input_variables"]

    def get_metadatas_as_dataframe(self) -> pd.DataFrame:
        """Gets metadatas from vectorstore objects and converts to dataframe.

        Returns:
            pd.DataFrame: metadatas.
        """
        metadatas = self._collection.get(include=["metadatas"])["metadatas"]
        metadatas_dataframe = pd.DataFrame(metadatas)
        return metadatas_dataframe
