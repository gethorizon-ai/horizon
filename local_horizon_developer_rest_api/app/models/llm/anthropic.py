from .base import BaseLLM
from langchain.llms import Anthropic as AnthropicOriginal
import anthropic


class Anthropic(BaseLLM, AnthropicOriginal):
    def get_model_name(self) -> str:
        return self.model

    def get_model_params_to_store(self) -> dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens_to_sample": self.max_tokens_to_sample,
        }

    @staticmethod
    def get_data_length(sample_str: str) -> int:
        return anthropic.count_tokens(sample_str)
