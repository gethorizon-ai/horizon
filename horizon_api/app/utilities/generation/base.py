"""Contains helper functions for prompt generation."""


def generate_input_variables_string(input_variables: list) -> str:
    """Returns string listing each input variable in angle brackets for use in prompt generation.

    Args:
        input_variables (list): list containing each input variable

    Returns:
        str: string listing each variable in angle brackets
    """
    input_variables_string = ", ".join(
        f"<{input_var}>" for input_var in input_variables
    )
    return input_variables_string


def generate_prompt_suffix(
    input_variables: list,
    include_context_from_data_repository: bool = False,
    few_shot_examples: bool = False,
) -> str:
    """Returns standard suffix to generated prompt prefix to hold input variables and prompt LLM for output.

    Args:
        input_variables (list): list containing each input variable
        include_context_from_data_repository (bool, optional): whether to include section for context from data repository. Defaults
            to False.
        few_shot_examples (bool, optional): whether prompt includes few shot examples. Only relevant if including context from data
            repository. Defaults to False.

    Returns:
        str: suffix string
    """
    # Include context from data repository if applicable
    if include_context_from_data_repository:
        if few_shot_examples:
            prompt_suffix = """\n\n==\nCONTEXT:\n\n{context}\n\n==\nBEGIN: Generate an output using the provided context and inputs while closely matching the tone and format of the prior examples.\n\n"""
        else:
            prompt_suffix = """\n\n==\nCONTEXT:\n\n{context}\n\n==\nBEGIN: Generate an output using the provided context and inputs.\n\n"""
    else:
        prompt_suffix = """\n\n==\nBEGIN:\n\n"""

    # Include input variables and output tag
    for input_var in input_variables:
        prompt_suffix += f"<{input_var}>: {{{input_var}}}\n"
    prompt_suffix += "<OUTPUT>:"

    return prompt_suffix
