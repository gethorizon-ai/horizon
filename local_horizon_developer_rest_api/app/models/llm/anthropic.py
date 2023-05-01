from .base import BaseLLM
from langchain.llms import ChatAnthropic as ChatAnthropicOriginal
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result
from typing import Any
import re


class ChatAnthropic(BaseLLM, ChatAnthropicOriginal):
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

    # Add retry functionality for Anthropic inference calls
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(6),
        # Retry only if error is not invalid API key (status code 401) or unprocessable entity (status code 422)
        retry=retry_if_result(
            lambda e: type(e) == anthropic.ApiException
            and int(re.search(r"status code: (\d+)", e.args[0]).group(1))
            not in [401, 422]
        ),
    )
    def generate(self, *args: Any, **kwargs: Any) -> Any:
        return super(ChatAnthropicOriginal, self).generate(*args, **kwargs)
