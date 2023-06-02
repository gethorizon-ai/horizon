from .base import BasePromptTemplate
from app.models.example_selector.max_marginal_relevance_example_selector import (
    MaxMarginalRelevanceExampleSelector,
)
from app.models.prompt import prompt
from app.models.vector_stores.pinecone import Pinecone
from langchain.prompts.few_shot import FewShotPromptTemplate as FewShotPromptOriginal


class FewshotPromptTemplate(BasePromptTemplate, FewShotPromptOriginal):
    def reconstruct_from_stored_data(
        evaluation_dataset_vector_db: Pinecone, template_data: dict
    ) -> "FewshotPromptTemplate":
        """Reconstructs a few shot prompt object from data stored.

        Args:
            dataset_file_path (str): path to evaluation dataset.
            template_data (dict): data to reconstruct few shot prompt template.
            openai_api_key (str): OpenAI API key to use for embeddings.

        Returns:
            FewshotPromptTemplate: few shot prompt object to be deployed.
        """
        example_selector = MaxMarginalRelevanceExampleSelector(
            vectorstore=evaluation_dataset_vector_db,
            k=template_data["k"],
            example_keys=template_data["input_variables"] + ["ground_truth"],
        )

        # Construct example prompt
        example_prompt = prompt.PromptTemplate(**template_data["example_prompt"])

        # Construct few shot prompt object
        return FewshotPromptTemplate(
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
        return {
            "example_prompt": self.example_prompt.to_dict(),
            "prefix": self.prefix,
            "suffix": self.suffix,
            "input_variables": self.input_variables,
            "k": self.example_selector.k,  # Number of few shot examples
        }
