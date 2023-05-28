"""Class to retry LLM if error occurs when parsing output."""

from .base import BaseParser
from langchain.output_parsers import (
    RetryWithErrorOutputParser as RetryWithErrorOutputParserOriginal,
)
from langchain.base_language import BaseLanguageModel
from langchain.chains.llm import LLMChain
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import (
    BaseOutputParser,
    OutputParserException,
    PromptValue,
)
from typing import TypeVar

T = TypeVar("T")

# Retry prompt that only shows error message, but not original prompt or completion. More useful in correcting JSON errors
RETRY_PROMPT = """You are a JSON error correction bot. The following output caused an error because it did not satisfy the requirements of the JSON schema. Correct the output to conform to the JSON schema.

<OUTPUT>: {completion}

<ERROR>: {error}

<CORRECTED JSON OUTPUT>:"""


class RetryWithErrorOutputParser(BaseParser, RetryWithErrorOutputParserOriginal):
    """Class to retry LLM if error occurs when parsing output."""

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        parser: BaseOutputParser[T],
        prompt: BasePromptTemplate = RETRY_PROMPT,
    ) -> RetryWithErrorOutputParser[T]:
        chain = LLMChain(llm=llm, prompt=prompt)
        return cls(parser=parser, retry_chain=chain)

    def parse(self, completion: str):
        try:
            print(f"Original completion: {completion}")
            parsed_completion = self.parser.parse(completion)
        except OutputParserException as e:
            print(f"Error: {repr(e)}")
            new_completion = self.retry_chain.run(completion=completion, error=repr(e))
            print(f"New completion: {new_completion}")
            parsed_completion = self.parser.parse(new_completion)

        return parsed_completion
