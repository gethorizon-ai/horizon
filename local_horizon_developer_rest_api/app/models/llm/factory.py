from typing import Type, Dict
from .base import BaseLLM
from .open_ai import (
    OpenAI,
    ChatOpenAI,
)


class LLMFactory:
    @staticmethod
    def create_llm(llm_type: str, **kwargs) -> BaseLLM:
        llm_classes = {
            "openai": OpenAI,
            "chat_openai": ChatOpenAI,
        }

        if llm_type not in llm_classes:
            raise ValueError(f"Invalid llm_type: {llm_type}")

        return llm_classes[llm_type](**kwargs)
