from .base import BasePromptTemplate
from app.models.example_selector.max_marginal_relevance_example_selector import (
    MaxMarginalRelevanceExampleSelector,
)
from app.models.vector_stores.pinecone import Pinecone
from app.utilities.dataset_processing import chunk
from langchain.prompts.prompt import PromptTemplate as PromptTemplateOriginal
from langchain.prompts.example_selector.base import BaseExampleSelector
from typing import Optional, Any


class PromptTemplate(BasePromptTemplate, PromptTemplateOriginal):
    context_selector: Optional[BaseExampleSelector] = None
    """ExampleSelector to retrieve context from data repository."""

    # def __init__(
    #     self,
    #     context_selector: Optional[BaseExampleSelector] = None,
    #     **kwargs,
    # ):
    #     """Setup ExampleSelector to retrieve context from data repository for QA use case, before passing to parent constructor.

    #     Args:
    #         context_selector (Optional[BaseExampleSelector], optional): ExampleSelector to retrieve context from data repository.
    #             Defaults to None.
    #     """
    #     print(f"Beginning to create prompt with {kwargs}")  # TODO: remove
    #     self.context_selector = context_selector
    #     print(f"Creating prompt with {kwargs}")  # TODO: remove
    #     super().__init__(**kwargs)

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
        return super().format(**kwargs)

    def reconstruct_from_stored_data(
        template_data: dict,
        vector_db_data_repository: Pinecone = None,
    ) -> "PromptTemplate":
        """Reconstructs prompt object from data stored.

        Args:
            template_data (dict): data to reconstruct prompt template.
            vector_db_evaluation_dataset (Pinecone, optional): vector db object for data repository. Defaults to None.

        Returns:
            PromptTemplate: prompt object to be deployed.
        """
        # Setup context selector if vector db for data repository provided
        context_selector = None
        if vector_db_data_repository:
            context_selector = MaxMarginalRelevanceExampleSelector(
                vectorstore=vector_db_data_repository,
                k=chunk.NUM_CHUNKS_TO_RETRIEVE_FOR_PROMPT_CONTEXT,
                example_keys=["context"],
                input_keys=template_data["input_variables"],
            )

        # Construct prompt object
        return PromptTemplate(
            context_selector=context_selector,
            template=template_data["template"],
            input_variables=template_data["input_variables"],
        )

    def to_dict(self):
        return {
            "template": self.template,
            "input_variables": self.input_variables,
        }
