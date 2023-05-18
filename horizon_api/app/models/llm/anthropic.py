from .base import BaseLLM
from app.models.llm.factory import LLMFactory
from langchain.chat_models import ChatAnthropic as ChatAnthropicOriginal
from langchain.schema import LLMResult
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result
from typing import Any
import re


class ChatAnthropic(BaseLLM, ChatAnthropicOriginal):
    def get_model_name(self) -> str:
        return self.model

    @staticmethod
    def get_data_length(sample_str: str) -> int:
        return anthropic.count_tokens(sample_str)

    def get_prompt_data_length(
        self, prompt_messages: list, llm_result: LLMResult
    ) -> int:
        prompt_string = self._convert_messages_to_prompt(prompt_messages)
        return anthropic.count_tokens(prompt_string)

    def get_completion_data_length(self, llm_result: LLMResult) -> int:
        completion_string = llm_result.generations[0][0].text
        return anthropic.count_tokens(completion_string)

    def get_model_params_to_store(self) -> dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens_to_sample": self.max_tokens_to_sample,
        }

    def set_temperature(self, temperature: float) -> None:
        self.temperature = temperature

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
