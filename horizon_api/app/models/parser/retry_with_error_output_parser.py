"""Class to retry LLM if error occurs when parsing output."""

from .base import BaseParser
from langchain.output_parsers import (
    RetryWithErrorOutputParser as RetryWithErrorOutputParserOriginal,
)
from langchain.prompts.base import StringPromptValue


class RetryWithErrorOutputParser(BaseParser, RetryWithErrorOutputParserOriginal):
    """Class to retry LLM if error occurs when parsing output."""

    def parse_with_prompt(self, completion: str, prompt_string: str):
        prompt_value = StringPromptValue(text=prompt_string)
        return super(RetryWithErrorOutputParserOriginal, self).parse_with_prompt(
            completion,
            prompt_value,
        )
