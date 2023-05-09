"""Class to parse LLM output according to given Pydantic object."""

from .base import BaseParser
from langchain.output_parsers import (
    PydanticOutputParser as PydanticOutputParserOriginal,
)
from langchain.schema import OutputParserException
import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class PydanticOutputParser(BaseParser, PydanticOutputParserOriginal):
    """Wrapper around LangChain PydanticOutputParser."""

    def get_format_instructions(self) -> str:
        """Returns output format instructions to append to prompt prefix.

        Currently, adds two newlines to standard response from LangChain original response.

        Returns:
            str: output format instructions to append to prompt prefix.
        """
        return (
            "\n\n==\nOUTPUT FORMAT:\n\n"
            + PydanticOutputParserOriginal.get_format_instructions(self)
            .replace("{", "{{")
            .replace("}", "}}")
        )
