"""Wrapper around LangChain Pinecone vector db object."""

from .base import BaseVectorStore
from langchain.vectorstores import Pinecone as PineconeOriginal
from langchain.vectorstores.utils import maximal_marginal_relevance
from typing import Any, Iterable, List, Optional, Dict
import uuid
import numpy as np

VECTOR_DIMENSIONS = 1536


class Pinecone(BaseVectorStore, PineconeOriginal):
    def __init__(
        self,
        input_variables: List[str] = None,
        num_unique_data: int = None,
        **kwargs,
    ):
        """Initializes object with custom fields and then calls parent constructor.

        Args:
            input_variables (List[str], optional): List of input variables. Defaults to None.
            num_unique_data (int, optional): Number of unique data points stored for user's namespace (without double counting across
                chunks of the same data). Defaults to None.
        """
        self.input_variables = input_variables
        self.num_unique_data = num_unique_data
        super().__init__(**kwargs)

    def add_text_embeddings_and_metadata(
        self,
        texts: Iterable[str],
        metadata: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 32,
    ) -> List[str]:
        """Embed texts and add associated ids, embeddings, and metadata to vectorstore without adding texts themselves.

        Not adding texts reduces memory required. This is useful when all the data in the text is captured in the metadata.

        Args:
            texts (Iterable[str]): Texts to add to the vectorstore.
            metadata (Optional[List[dict]], optional): Optional list of metadata.
            ids (Optional[List[str]], optional): Optional list of IDs.
            batch_size (int, optional): batch size for upserting vectors. Defaults to 32.

        Returns:
            List[str]: List of IDs of the added texts.
        """
        # Embed and create the documents. Do not upload the actual text since all the data is in the metadata
        docs = []
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        for i, text in enumerate(texts):
            embedding = self._embedding_function(text)
            metadata_item = metadata[i] if metadata else {}
            docs.append((ids[i], embedding, metadata_item))

        # upsert to Pinecone
        self._index.upsert(
            vectors=docs,
            namespace=self._namespace,
            batch_size=batch_size,
        )
        return ids

    def get_namespace(self) -> str:
        """Returns namespace.

        Returns:
            str: namespace.
        """
        return self._namespace

    def get_input_variables(self) -> List[str]:
        """Returns list of input variables.

        Returns:
            list: list of input variables.
        """
        return self.input_variables

    def get_num_unique_data(self) -> int:
        """Returns number of unique data points (i.e., rows in evaluation dataset before chunking).

        Returns:
            int: number of unique data points.
        """
        return self.num_unique_data

    def get_data_per_evaluation_data_id(
        self,
        evaluation_data_id_list: List[int],
        query: str = None,
        include_embeddings: bool = True,
        include_metatata: bool = True,
        include_evaluation_data_id_in_metadata: bool = True,
        include_input_variables_in_metadata: bool = True,
        include_ground_truth_in_metadata: bool = True,
    ) -> dict:
        """Fetches db record for each of the provided evaluation data ids that is most similar to given query string, then returns
        consolidated list of db ids, metadata, and embeddings across all the fetched records.

        If query string is not provided, then just fetches first db record for each of the provided evaluation data ids. This can be
        used to get the ground truth for each evaluation data id (which should be the same across all chunks).

        Options to exclude to metadata or embeddings for increased efficiency.

        Args:
            query (str): query to find most similar db entry.
            evaluation_data_id_list (List[int]): list of evaluation data ids for which to fetch one db record each.
            include_embeddings (bool, optional): whether to fetch embeddings from vector db. Defaults to True.
            include_metadata (bool, optional): whether to fetch metadata from vector db. Defaults to True.
            include_evaluation_data_id_in_metadata (bool, optional): whether to include "evaluation_data_id" key in metadata.
                Defaults to True.
            include_input_variables_in_metadata (bool, optional): whether to include input variable keys in metadata. Defaults to
                True.
            include_ground_truth_in_metadata (bool, optional): whether to include "ground_truth" key in metadata. Defaults to True.

        Returns:
            dict: consolidated list of db ids, metadata, and embeddings.
        """
        # Embed query if provided
        if query:
            query_embedding = self._embedding_function(query)
        # Otherwise, use zero vector
        else:
            query_embedding = [0] * VECTOR_DIMENSIONS

        # Create lists to store combined results from db pull
        combined_ids = []
        if include_embeddings:
            combined_embeddings = []
        if include_metatata:
            combined_metadata = []

        # Fetch db record for each evaluation data id that is most similar to query, then add to combined list
        # If no query string is provided, then fetch first db record for each of the provided evaluation data ids
        for id in evaluation_data_id_list:
            db_result = self._index.query(
                vector=query_embedding,
                filter={"evaluation_data_id": id},
                top_k=1,
                namespace=self._namespace,
                include_values=include_embeddings,
                include_metadata=include_metatata,
            )
            fetched_data = db_result["matches"][0]

            combined_ids.append(fetched_data["id"])
            if include_embeddings:
                combined_embeddings.append(fetched_data["values"])
            if include_metatata:
                combined_metadata.append(fetched_data["metadata"])

        if include_metatata:
            # Remove evaluation_data_id key in metadata if requested
            if not include_evaluation_data_id_in_metadata:
                for metadata in combined_metadata:
                    del metadata["evaluation_data_id"]

            # Remove input values in metadata if requested
            if not include_input_variables_in_metadata:
                input_variables = self.get_input_variables()
                for metadata in combined_metadata:
                    for var in input_variables:
                        del metadata[var]

            # Remove ground truth in metadata if requested
            if not include_ground_truth_in_metadata:
                for metadata in combined_metadata:
                    del metadata["ground_truth"]

        # Package combined results into single dict
        combined_db_result = {"ids": combined_ids}
        if include_embeddings:
            combined_db_result["embeddings"] = combined_embeddings
        if include_metatata:
            combined_db_result["metadata"] = combined_metadata

        return combined_db_result

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        filter_statement: dict = None,
        lambda_mult: float = 0.5,
    ) -> List[Dict[str, str]]:
        """Return metadata selected using maximal marginal relevance.

        Maximal marginal relevance optimizes for similarity to query and diversity among selected items.

        Args:
            query (str): text for which to pull similar metadata.
            k (int, optional): number of metadata to return. Defaults to 4.
            fetch_k (int, optional): number of metadata to pass to max marginal relevance algorithm. Defaults to 20.
            filter_statement (dict, optional): statement to filter metadata pulled. Defaults to None.
            lambda_mult (float, optional): Number between 0 and 1 that determines the degree of diversity among the results with 0
                corresponding to maximum diversity and 1 to minimum diversity. Defaults to 0.5.

        Raises:
            ValueError: checks if embedding function exists to pull metadata.

        Returns:
            Dict[str, str]: list of metadata.
        """
        if self._embedding_function is None:
            raise ValueError(
                "For MMR search, you must specify an embedding function on creation."
            )

        # Embed query
        query_embedding = self._embedding_function(query)

        # Fetch results from vector db
        db_result = self._index.query(
            vector=query_embedding,
            filter=filter_statement,
            top_k=fetch_k,
            namespace=self._namespace,
            include_values=True,
            include_metadata=True,
        )

        # Aggregate embeddings across all matches returned from db
        embeddings = [
            db_result["matches"][i]["values"] for i in range(len(db_result["matches"]))
        ]

        # Select results using max marginal relevance
        mmr_selected = maximal_marginal_relevance(
            np.array(query_embedding, dtype=np.float32),
            embeddings,
            k=k,
            lambda_mult=lambda_mult,
        )

        # Filter to results selected by max marginal relevance
        selected_results = [db_result["matches"][i]["metadata"] for i in mmr_selected]
        return selected_results

    def delete_namespace(self) -> None:
        """Deletes all vectors and metadata in namespace."""
        self._index.delete(
            deleteAll=True,
            namespace=self._namespace,
        )
