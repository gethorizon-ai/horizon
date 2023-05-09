"""Class to parse LLM output according to given Pydantic object."""

from .base import BaseParser
from langchain.output_parsers import (
    PydanticOutputParser as PydanticOutputParserOriginal,
)


class PydanticOutputParser(BaseParser, PydanticOutputParserOriginal):
    """Wrapper around LangChain PydanticOutputParser."""

    def get_format_instructions(self) -> str:
        """Returns output format instructions to append to prompt prefix.

        Currently, adds two newlines to standard response from LangChain original response.

        Returns:
            str: output format instructions to append to prompt prefix.
        """
        print("Got request to get output format instructions")
        print(
            f"Standard output format instructions: {PydanticOutputParserOriginal.get_format_instructions(self)}"
        )
        return "\n\n" + PydanticOutputParserOriginal.get_format_instructions(
            self
        ).replace("{", "{{").replace("}", "}}")
