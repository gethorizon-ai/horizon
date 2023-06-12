from .base import BasePromptTemplate
from app.models.example_selector.max_marginal_relevance_example_selector import (
    MaxMarginalRelevanceExampleSelector,
)
from app.models.prompt import prompt
from app.models.vector_stores.pinecone import Pinecone
from app.utilities.dataset_processing import chunk
from langchain.prompts.few_shot import FewShotPromptTemplate as FewShotPromptOriginal
from langchain.prompts.example_selector.base import BaseExampleSelector
from typing import Optional, Any


class FewshotPromptTemplate(BasePromptTemplate, FewShotPromptOriginal):
    context_selector: Optional[BaseExampleSelector] = None
    """ExampleSelector to retrieve context from data repository."""

    def format_with_context(self, **kwargs: Any) -> str:
        """First populate the prompt with context from data repository if applicable, then format the prompt with the inputs.

        Args:
            kwargs: Any arguments to be passed to the prompt template.

        Returns:
            A formatted string.
        """
        # If applicable, retrieve context and setup partial prompt with context. Then format rest of prompt
        if self.context_selector:
            # Retrieve context
            context_chunks = self.context_selector.select_examples(kwargs)
            context = "\n".join([chunk["context"] for chunk in context_chunks])

            # Update prompt input and partial variables
            self.input_variables = list(
                set(self.input_variables).difference(set(["context"]))
            )
            self.partial_variables = {**self.partial_variables, **{"context": context}}

        # Format remainder of prompt
        output = super().format(**kwargs)

        # Reset partial and input variables
        self.input_variables.extend(self.partial_variables.keys())
        self.partial_variables = {}

        # Return output
        return output

    def reconstruct_from_stored_data(
        template_data: dict,
        vector_db_evaluation_dataset: Pinecone,
        vector_db_data_repository: Pinecone = None,
    ) -> "FewshotPromptTemplate":
        """Reconstructs a few shot prompt object from data stored.

        Args:
            template_data (dict): data to reconstruct few shot prompt template.
            vector_db_evaluation_dataset (Pinecone): vector db object for evaluation dataset.
            vector_db_evaluation_dataset (Pinecone, optional): vector db object for data repository. Defaults to None.

        Returns:
            FewshotPromptTemplate: few shot prompt object to be deployed.
        """
        # Setup context selector if vector db for data repository provided. Add "context" as input variable
        context_selector = None
        if vector_db_data_repository:
            context_selector = MaxMarginalRelevanceExampleSelector(
                vectorstore=vector_db_data_repository,
                k=chunk.NUM_CHUNKS_TO_RETRIEVE_FOR_PROMPT_CONTEXT,
                example_keys=["context"],
                input_keys=template_data["input_variables"],
            )
            template_data["input_variables"].append("context")

        # Setup few shot example selector. Remove "context" as input variable in case it was added
        example_selector = MaxMarginalRelevanceExampleSelector(
            vectorstore=vector_db_evaluation_dataset,
            k=template_data["k"],
            example_keys=template_data["input_variables"] + ["ground_truth"],
            input_keys=list(
                set(template_data["input_variables"]).difference(set(["context"]))
            ),
        )

        # Construct example prompt
        example_prompt = prompt.PromptTemplate(**template_data["example_prompt"])

        print(
            f"Template data when reconstructing prompt: {template_data}"
        )  # TODO: remove

        # Construct few shot prompt object
        return FewshotPromptTemplate(
            context_selector=context_selector,
            example_selector=example_selector,
            example_prompt=example_prompt,
            prefix=template_data["prefix"],
            suffix=template_data["suffix"],
            input_variables=template_data["input_variables"],
        )

    def to_dict(self) -> dict:
        """Return dict with information to reconstruct few-shot prompt template.

        Returns:
            dict: information to reconstruct few-shot prompt template.
        """
        # Remove "context" from input variables list since that is not input provided by user
        return {
            "example_prompt": self.example_prompt.to_dict(),
            "prefix": self.prefix,
            "suffix": self.suffix,
            "input_variables": list(
                set(self.input_variables).difference(set(["context"]))
            ),
            "k": self.example_selector.k,  # Number of few shot examples
        }
