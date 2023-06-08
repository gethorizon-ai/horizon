"""Class to retry LLM if error occurs when parsing output."""

from .base import BaseParser
from langchain.base_language import BaseLanguageModel
from langchain.chains.llm import LLMChain
from langchain.prompts.prompt import PromptTemplate

from langchain.schema import BaseOutputParser, OutputParserException
from typing import TypeVar

T = TypeVar("T")

# Retry prompt that shows error and original output
RETRY_WITH_ERROR_PROMPT = PromptTemplate.from_template(
    """You are a JSON error correction bot. The following output caused an error because it did not satisfy the requirements of the JSON schema. Correct the output to conform to the JSON schema while staying as close to the original output as possible.

<ERROR>: {error}

<ORIGINAL OUTPUT>: {completion}

<CORRECTED JSON OUTPUT>:"""
)

# Retry prompt that shows JSON schema and original output
RETRY_WITH_SCHEMA_PROMPT = PromptTemplate.from_template(
    """You are a JSON error correction bot. The following output caused an error because it did not satisfy the requirements of the JSON schema. Correct the output to conform to the JSON schema while staying as close to the original output as possible.

<JSON SCHEMA>: {schema}

<ORIGINAL OUTPUT>: {completion}

<CORRECTED JSON OUTPUT>:"""
)


class RetryOutputParser(BaseParser):
    """Class to retry LLM if error occurs when parsing output."""

    def __init__(
        self,
        llm: BaseLanguageModel,
        parser: BaseOutputParser[T],
    ) -> None:
        self.parser = parser
        self.schema = self.parser.get_format_instructions(schema_only=True)
        self.retry_with_error_chain = LLMChain(
            llm=llm,
            prompt=RETRY_WITH_ERROR_PROMPT,
        )
        self.retry_with_schema_chain = LLMChain(
            llm=llm,
            prompt=RETRY_WITH_SCHEMA_PROMPT,
        )

    def parse(self, completion: str, prompt_string: str) -> str:
        """Tries to parse given completion and, if error, retries up to 2 times to correct JSON format.

        First retry includes error and original completion. Second retry includes JSON schema and original completion.

        Args:
            completion (str): original completion string.

        Returns:
            str: completion string in correct JSON format.
        """
        max_retries = 2

        try:
            print(f"Original completion: {completion}")
            parsed_completion = self.parser.parse(completion)

        except OutputParserException as e:
            print(f"Error: {str(e)}")
            for i in range(max_retries):
                try:
                    if i == 0:
                        new_completion = self.retry_with_error_chain.run(
                            error=str(e),
                            completion=completion,
                        )
                    elif i == 1:
                        new_completion = self.retry_with_schema_chain.run(
                            schema=self.schema,
                            completion=completion,
                        )
                    print(f"New completion: {new_completion}")
                    parsed_completion = self.parser.parse(new_completion)
                    break

                except:
                    if i == max_retries - 1:
                        raise Exception(str(e))
                    else:
                        continue

        return parsed_completion
