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

    def parse(self, text: str) -> T:
        """Re-implemented LangChain parse function to change json.loads to strict=False so that control characters (e.g., newlines)
        are accepted.

        Args:
            text (str): output from llm to parse.

        Raises:
            OutputParserException: error when output cannot parsed according to output schema.

        Returns:
            T: Pydantic model object.
        """
        print("THIS METHOD WAS CALLED!")
        try:
            # Greedy search for 1st json candidate.
            match = re.search(
                r"\{.*\}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
            )
            json_str = ""
            if match:
                json_str = match.group()
            json_object = json.loads(json_str, strict=False)  # Edited to strict=False
            return self.pydantic_object.parse_obj(json_object)

        except (json.JSONDecodeError, ValidationError) as e:
            name = self.pydantic_object.__name__
            msg = f"Failed to parse {name} from completion {text}. Got: {e}"
            raise OutputParserException(msg)
