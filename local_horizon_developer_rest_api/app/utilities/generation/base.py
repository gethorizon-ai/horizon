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


def generate_prompt_suffix(input_variables: list) -> str:
    """Returns standard suffix to generated prompt prefix to hold input variables and prompt LLM for output.

    Args:
        input_variables (list): list containing each input variable

    Returns:
        str: suffix string
    """
    prompt_suffix = """\n\n==\nBEGIN:\n\n"""
    for input_var in input_variables:
        prompt_suffix += f"<{input_var}>: {{{input_var}}}\n"
    prompt_suffix += "<OUTPUT>:"
    return prompt_suffix
