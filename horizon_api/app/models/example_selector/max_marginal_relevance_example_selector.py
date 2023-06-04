"""Wrapper around LangChain max marginal relevance example selector to work properly with our vector db schema."""

from .base import BaseExampleSelector
from langchain.prompts.example_selector import (
    MaxMarginalRelevanceExampleSelector as MaxMarginalRelevanceExampleSelectorOriginal,
)
from typing import Dict, List


class MaxMarginalRelevanceExampleSelector(
    BaseExampleSelector, MaxMarginalRelevanceExampleSelectorOriginal
):
    # Filter statement in vector db search. Can be used to filter to subset of evaluation dataset (e.g., training data)
    filter_statement: dict = None

    def select_examples(self, input_variables: Dict[str, str]) -> List[dict]:
        """Gets examples that optimize for max marginal relevance to given input values.

        Args:
            input_variables (Dict[str, str]): value for each input variable.

        Returns:
            List[dict]: selected examples.
        """
        if self.input_keys:
            input_variables = {key: input_variables[key] for key in self.input_keys}

        # Changed query string from LangChain implementation to match format of initial embedding of evaluation dataset into vector db
        query = "\n".join(
            [f"<{key}>: {value}" for key, value in input_variables.items()]
        )

        print(f"About to get few shot examples with this query: {query}")

        # Get the examples from the metadata.
        # This assumes that examples are stored in metadata.
        examples = self.vectorstore.max_marginal_relevance_search(
            query,
            k=self.k,
            fetch_k=self.fetch_k,
            filter_statement=self.filter_statement,
        )

        print(f"Retrived {len(examples)} few shot examples")

        # If example keys are provided, filter examples to those keys.
        if self.example_keys:
            examples = [{k: eg[k] for k in self.example_keys} for eg in examples]

        return examples
