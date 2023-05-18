from app.models.llm.factory import LLMFactory


def calculate_cost(llm_type: str, prompt_chars: int, completion_chars: int) -> float:
    if llm_type not in LLMFactory.llm_classes:
        raise ValueError(f"Invalid llm_type: {llm_type}")

    if LLMFactory.llm_classes[llm_type]["data_unit"] == "token":
        # Fetch the prices
        price_per_prompt_token = LLMFactory.llm_classes[llm_type][
            "price_per_data_unit_prompt"
        ]
        price_per_completion_token = LLMFactory.llm_classes[llm_type][
            "price_per_data_unit_completion"
        ]

        # Fetch the token per character ratio
        tokens_per_char = LLMFactory.llm_data_assumptions["tokens_per_character"]

        # Calculate the number of tokens
        prompt_tokens = prompt_chars * tokens_per_char
        completion_tokens = completion_chars * tokens_per_char

        # Calculate the cost
        cost = (
            prompt_tokens * price_per_prompt_token
            + completion_tokens * price_per_completion_token
        )

    elif LLMFactory.llm_classes[llm_type]["data_unit"] == "character":
        # Fetch the prices
        price_per_prompt_char = LLMFactory.llm_classes[llm_type][
            "price_per_data_unit_prompt"
        ]
        price_per_completion_char = LLMFactory.llm_classes[llm_type][
            "price_per_data_unit_completion"
        ]

        # Calculate the cost
        cost = (
            prompt_chars * price_per_prompt_char
            + completion_chars * price_per_completion_char
        )

    return cost
