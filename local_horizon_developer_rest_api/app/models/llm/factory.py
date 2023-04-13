from typing import Type, Dict
from .base import BaseLLM
from .open_ai import (
    OpenAI,
    ChatOpenAI,
)


class LLMFactory:
    llm_classes = {
        "gpt-3.5-turbo": {
            "class": ChatOpenAI,
            "data_unit": "token",
            "data_limit": 4096,
            "encoding": "cl100k_base",
            "price_per_data_unit": 0.002 / 1000,
        },
        "text-davinci-003": {
            "class": OpenAI,
            "data_unit": "token",
            "data_limit": 4097,
            "encoding": "p50k_base",
            "price_per_data_unit": 0.02 / 1000,
        },
    }

    # Assumptions for llm data input / output
    llm_data_assumptions = {
        "tokens_per_character": 0.3,  # assumes 0.75 words / token and 4.7 characters / word
        "instruction_tokens": 250,
        "instruction_characters": 250 / 0.3,
        "input_output_multiplier": 1.1,  # multiplier for input and output data length as buffer
        "buffer_tokens": 250,
        "buffer_characters": 250 / 0.3,
    }

    @staticmethod
    def create_llm(llm_type: str, **kwargs) -> BaseLLM:
        if llm_type not in LLMFactory.llm_classes:
            raise ValueError(f"Invalid llm_type: {llm_type}")

        return LLMFactory.llm_classes[llm_type]["class"](**kwargs)
