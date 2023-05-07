from langchain.llms import OpenAI as OpenAIOriginal
from langchain.chat_models import ChatOpenAI as ChatOpenAIOriginal
from .base import BaseLLM
import tiktoken
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
import openai
from typing import Any


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

    # Add additional retry functionality for OpenAI inference calls
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(6),
        # Retry only if error is not invalid API key (status code 401) or unprocessable entity (status code 422)
        retry=(
            retry_if_exception_type(openai.error.Timeout)
            | retry_if_exception_type(openai.error.APIError)
            | retry_if_exception_type(openai.error.APIConnectionError)
            | retry_if_exception_type(openai.error.RateLimitError)
            | retry_if_exception_type(openai.error.ServiceUnavailableError)
        ),
    )
    def generate(self, *args: Any, **kwargs: Any) -> Any:
        return super(OpenAIOriginal, self).generate(*args, **kwargs)


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

    # Add additional retry functionality for OpenAI inference calls
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(6),
        # Retry only if error is not invalid API key (status code 401) or unprocessable entity (status code 422)
        retry=(
            retry_if_exception_type(openai.error.Timeout)
            | retry_if_exception_type(openai.error.APIError)
            | retry_if_exception_type(openai.error.APIConnectionError)
            | retry_if_exception_type(openai.error.RateLimitError)
            | retry_if_exception_type(openai.error.ServiceUnavailableError)
        ),
    )
    def generate(self, *args: Any, **kwargs: Any) -> Any:
        return super(ChatOpenAIOriginal, self).generate(*args, **kwargs)
