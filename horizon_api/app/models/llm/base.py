from abc import ABC, abstractmethod
from typing import Any, List


class BaseLLM(ABC):
    @abstractmethod
    def get_model_name(self) -> str:
        """Return the name of the model object.

        Returns:
            str: name of the model object
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
