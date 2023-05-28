"""Class to retry LLM if error occurs when parsing output."""

from .base import BaseParser
from langchain.output_parsers import (
    RetryWithErrorOutputParser as RetryWithErrorOutputParserOriginal,
)

from langchain.schema import OutputParserException
from typing import TypeVar

T = TypeVar("T")


class RetryWithErrorOutputParser(BaseParser, RetryWithErrorOutputParserOriginal):
    """Class to retry LLM if error occurs when parsing output."""

    def parse(self, completion: str) -> str:
        """Tries to parse given completion and, if error, tries to correct JSON format.

        Args:
            completion (str): original completion string.

        Returns:
            str: completion string in correct JSON format.
        """
        try:
            print(f"Original completion: {completion}")
            parsed_completion = self.parser.parse(completion)
        except OutputParserException as e:
            print(f"Error: {str(e)}")
            new_completion = self.retry_chain.run(completion=completion, error=str(e))
            print(f"New completion: {new_completion}")
            parsed_completion = self.parser.parse(new_completion)

        return parsed_completion
