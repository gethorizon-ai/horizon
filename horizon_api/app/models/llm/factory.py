from .base import BaseLLM
from .open_ai import (
    OpenAI,
    ChatOpenAI,
)
from .anthropic import ChatAnthropic


class LLMFactory:
    llm_classes = {
        "gpt-3.5-turbo": {
            "class": ChatOpenAI,
            "provider": "OpenAI",
            "data_unit": "token",
            "data_limit": 4096,
            "price_per_data_unit_prompt": 0.0015 / 1000,
            "price_per_data_unit_completion": 0.002 / 1000,
        },
        "text-davinci-003": {
            "class": OpenAI,
            "provider": "OpenAI",
            "data_unit": "token",
            "data_limit": 4097,
            "price_per_data_unit_prompt": 0.02 / 1000,
            "price_per_data_unit_completion": 0.02 / 1000,
        },
        "claude-instant-v1": {
            "class": ChatAnthropic,
            "provider": "Anthropic",
            "data_unit": "token",
            "data_limit": 9000,
            "price_per_data_unit_prompt": 1.63 / 1000000,
            "price_per_data_unit_completion": 5.51 / 1000000,
        },
        "claude-v1": {
            "class": ChatAnthropic,
            "provider": "Anthropic",
            "data_unit": "token",
            "data_limit": 9000,
            "price_per_data_unit_prompt": 11.02 / 1000000,
            "price_per_data_unit_completion": 32.68 / 1000000,
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
        "min_max_output_tokens": 250,  # min value for max output tokens
        "min_max_output_characters": 250 / 0.3,
        "max_few_shots": 10,  # max number of few shot examples allowed
    }

    @staticmethod
    def create_llm(llm_type: str, **kwargs) -> BaseLLM:
        if llm_type not in LLMFactory.llm_classes:
            raise ValueError(f"Invalid llm_type: {llm_type}")

        return LLMFactory.llm_classes[llm_type]["class"](**kwargs)

    @staticmethod
    def create_model_params(
        llm: str, max_output_length: int, llm_api_key: str, temperature: float = 0.7
    ) -> dict:
        if LLMFactory.llm_classes[llm]["provider"] == "OpenAI":
            model_params = {
                "model_name": llm,
                "temperature": temperature,
                "max_tokens": max_output_length,
                "openai_api_key": llm_api_key,
            }
        elif LLMFactory.llm_classes[llm]["provider"] == "Anthropic":
            model_params = {
                "model": llm,
                "temperature": temperature,
                "max_tokens_to_sample": max_output_length,
                "anthropic_api_key": llm_api_key,
            }

        return model_params

    @staticmethod
    def get_data_unit(model_name: str) -> str:
        return LLMFactory.llm_classes[model_name]["data_unit"]

    @staticmethod
    def get_prompt_cost(model_name: str, prompt_data_length: int) -> float:
        return (
            prompt_data_length
            * LLMFactory.llm_classes[model_name]["price_per_data_unit_prompt"]
        )

    @staticmethod
    def get_completion_cost(model_name: str, completion_data_length: int) -> float:
        return (
            completion_data_length
            * LLMFactory.llm_classes[model_name]["price_per_data_unit_completion"]
        )
