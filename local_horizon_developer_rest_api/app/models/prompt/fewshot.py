from .base import BasePromptTemplate
from app.models.prompt import prompt
from app.utilities.dataset_processing import dataset_processing
from langchain.prompts.few_shot import FewShotPromptTemplate as FewShotPromptOriginal
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts.example_selector import MaxMarginalRelevanceExampleSelector


class FewshotPromptTemplate(BasePromptTemplate, FewShotPromptOriginal):
    def reconstruct_from_stored_data(
        dataset_file_path: str, template_data: dict, openai_api_key: str
    ) -> "FewshotPromptTemplate":
        """Reconstructs a few shot prompt object from data stored.

        Args:
            dataset_file_path (str): path to evaluation dataset.
            template_data (dict): data to reconstruct few shot prompt template.
            openai_api_key (str): user's OpenAI API key.

        Returns:
            FewshotPromptTemplate: few shot prompt object to be deployed.
        """
        # Get evaluation dataset and convert each row to dict
        evaluation_dataset = dataset_processing.get_evaluation_dataset(
            dataset_file_path=dataset_file_path
        )
        evaluation_dataset = evaluation_dataset.drop("evaluation_data_id", axis=1)
        examples = evaluation_dataset.to_dict("records")

        # Construct example selector
        example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
            examples,
            OpenAIEmbeddings(openai_api_key=openai_api_key),
            FAISS,
            k=template_data["k"],
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
