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

    def get_data_per_evaluation_data_id(
        self,
        evaluation_data_id_list: List[int],
        query: str = None,
        include_embeddings: bool = True,
        include_metatatas: bool = True,
        include_evaluation_data_id_in_metadatas: bool = True,
        include_input_variables_in_metadatas: bool = True,
        include_ground_truth_in_metadatas: bool = True,
    ) -> dict:
        """Fetches db record for each of the provided evaluation data ids that is most similar to given query string, then returns
        consolidated list of chroma ids, metadatas, and embeddings across all the fetched records.

        If query string is not provided, then just fetches random db record for each of the provided evaluation data ids. This can be
        used to get the ground truth for each evaluation data id (which should be the same across all chunks).

        Option to exclude to metadatas or embeddings for increased efficiency.

        Args:
            query (str): query to find most similar db entry.
            evaluation_data_id_list (List[int]): list of evaluation data ids for which to fetch one db record each.
            include_evaluation_data_id_in_metadatas (bool, optional): whether to include "evaluation_data_id" key in metadatas.
                Defaults to True.
            include_input_variables_in_metadatas (bool, optional): whether to include input variable keys in metadatas. Defaults to
                True.
            include_ground_truth_in_metadatas (bool, optional): whether to include "ground_truth" key in metadatas. Defaults to True.

        Returns:
            dict: consolidated list of chroma ids, metadatas, and embeddings.
        """
        # Embed query if provided
        if query:
            query_embedding = self._embedding_function.embed_query(query)

        # Create include statement for and lists to store combined results from db pull
        include_statement = []
        combined_ids = []
        if include_embeddings:
            include_statement.append("embeddings")
            combined_embeddings = []
        if include_metatatas:
            include_statement.append("metadatas")
            combined_metadatas = []

        # Fetch db record for each evaluation data id that is most similar to query, then add to combined list
        # If no query is provided, then fetch random db record for each of the provided evaluation data ids
        for id in evaluation_data_id_list:
            if query:
                db_result = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=1,
                    where={"evaluation_data_id": id},
                    include=include_statement,
                )
            else:
                db_result = self._collection.get(
                    where={"evaluation_data_id": id},
                    limit=1,
                    include=include_statement,
                )

            combined_ids.append(db_result["ids"])
            if include_embeddings:
                combined_embeddings.append(db_result["embeddings"])
            if include_metatatas:
                combined_metadatas.append(db_result["metadatas"])

        if include_metatatas:
            # Remove evaluation_data_id key in metadatas if requested
            if not include_evaluation_data_id_in_metadatas:
                for metadata in combined_metadatas:
                    del metadata["evaluation_data_id"]

            # Remove input values in metadatas if requested
            if not include_input_variables_in_metadatas:
                input_variables = self.get_input_variables_from_collection_metadata()
                for metadata in combined_metadatas:
                    for var in input_variables:
                        del metadata[var]

            # Remove ground truth in metadatas if requested
            if not include_ground_truth_in_metadatas:
                for metadata in combined_metadatas:
                    del metadata["ground_truth"]

        combined_db_result = {"ids": combined_ids}
        if include_embeddings:
            combined_db_result["embeddings"] = combined_embeddings
        if include_metatatas:
            combined_db_result["metadatas"] = combined_metadatas

        return combined_db_result
