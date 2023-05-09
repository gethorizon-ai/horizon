"""Class to retry LLM if error occurs when parsing output."""

from .base import BaseParser
from langchain.output_parsers import (
    RetryWithErrorOutputParser as RetryWithErrorOutputParserOriginal,
)


class RetryWithErrorOutputParser(BaseParser, RetryWithErrorOutputParserOriginal):
    """Class to retry LLM if error occurs when parsing output."""

    pass
