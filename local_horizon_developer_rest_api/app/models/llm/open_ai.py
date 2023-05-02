from langchain.llms import OpenAI as OpenAIOriginal
from langchain.chat_models import ChatOpenAI as ChatOpenAIOriginal
from .base import BaseLLM
import tiktoken


class OpenAI(BaseLLM, OpenAIOriginal):
    def get_model_name(self) -> str:
        return self.model_name

    @staticmethod
    def get_data_length(sample_str: str) -> int:
        encoding_davinci = tiktoken.encoding_for_model("text-davinci-003")
        return len(encoding_davinci.encode(sample_str))

    def get_model_params_to_store(self) -> dict:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


class ChatOpenAI(BaseLLM, ChatOpenAIOriginal):
    def get_model_name(self) -> str:
        return self.model_name

    @staticmethod
    def get_data_length(sample_str: str) -> int:
        encoding_turbo = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding_turbo.encode(sample_str))

    def get_model_params_to_store(self) -> dict:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
