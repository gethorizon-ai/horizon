from abc import ABC, abstractmethod
from typing import Any, List
from langchain.schema import LLMResult


class BaseLLM(ABC):
    @abstractmethod
    def get_model_name(self) -> str:
        """Return the name of the model object.

        Returns:
            str: name of the model object
        """
        pass

    @abstractmethod
    def get_data_unit(self) -> str:
        """Get data unit for model pricing (e.g., token, character).

        Returns:
            str: data unit for model pricing.
        """
        pass

    @abstractmethod
    def get_data_length(sample_str: str) -> int:
        """Evaluates data length of the given string based on the model's data unit (e.g., tokens, characters) and encoder (if
        applicable).

        Args:
            sample_str (str): string for which assess data length.

        Returns:
            int: length of data in string.
        """
        pass

    @abstractmethod
    def get_prompt_data_length(
        self, prompt_messages: list, llm_result: LLMResult
    ) -> int:
        """Get prompt data length (e.g., number of tokens, characters).

        Args:
            prompt_messages (list): prompt messages passed into llm.
            llm_result (LLMResult): generation result from the llm object.

        Returns:
            int: prompt data length.
        """
        pass

    @abstractmethod
    def get_completion_data_length(self, llm_result: LLMResult) -> int:
        """Get completion data length (e.g., number of tokens, characters).

        Args:
            llm_result (LLMResult): generation result from the llm object.

        Returns:
            int: completion data length.
        """
        pass

    @abstractmethod
    def get_prompt_cost(self, prompt_data_length: int) -> float:
        """Get llm provider cost for prompt data.

        Args:
            prompt_data_length (int): prompt data length (e.g., number of tokens, characters).

        Returns:
            float: prompt cost.
        """
        pass

    @abstractmethod
    def get_completion_cost(self, completion_data_length: int) -> float:
        """Get llm provider cost for completion data.

        Args:
            completion_data_length (int): completion data length (e.g., number of tokens, characters).

        Returns:
            float: completion cost.
        """
        pass

    @abstractmethod
    def get_model_params_to_store(self) -> dict:
        """Outputs model parameters that can be stored in db to later reconstruct model.

        Make sure to not store user's llm api key!"""
        pass

    @abstractmethod
    def set_temperature(self, temperature: float) -> None:
        """Updates model temperature in llm object.

        Args:
            temperature (float): new temperature for llm.
        """
        pass
