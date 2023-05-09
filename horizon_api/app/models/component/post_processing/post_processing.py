"""Data structure to track post-processing operations."""

from app.models.llm.base import BaseLLM
from app.models.parser.pydantic_output_parser import PydanticOutputParser
from app.models.parser.retry_with_error_output_parser import RetryWithErrorOutputParser
from app.utilities.S3.s3_util import download_file_from_s3_and_save_locally
from app.utilities.output_schema import output_schema
from langchain.prompts.base import StringPromptValue
from pydantic import BaseModel


# Final output value if unable to align llm output with output schema requirements
FINAL_ERROR_MESSAGE = (
    "Error - failed to generate output satisfying output schema requirements."
)


class PostProcessing:
    """Data structure to track post-processing operations."""

    def __init__(self, pydantic_model_s3_key: str, llm: BaseLLM = None):
        """Initializes PostProcessing data structure.

        Args:
            pydantic_model_s3_key (str): s3 key for pydantic model of output schema.
            llm (BaseLLM, optional): LLM object to use when retrying with output errors. Defaults to None.
        """
        self.pydantic_object = output_schema.get_pydantic_object_from_s3(
            pydantic_model_s3_key=pydantic_model_s3_key
        )
        self.pydantic_output_parser = PydanticOutputParser(
            pydantic_object=self.pydantic_object
        )
        self.output_format_instructions = (
            self.pydantic_output_parser.get_format_instructions()
        )

        # Initialize RetryWithErrorOutputParser if llm object provided
        self.retry_with_error_output_parser = None
        if llm:
            self.retry_with_error_output_parser = RetryWithErrorOutputParser(
                parser=self.pydantic_output_parser, llm=llm
            )

    def update_llm_for_retry_with_error_output_parser(self, llm: BaseLLM):
        """Update or initialize RetryWithErrorOutputParser using provided llm object.

        Args:
            llm (BaseLLM): LLM object to use when retrying with output errors.
        """
        self.retry_with_error_output_parser = RetryWithErrorOutputParser(
            parser=self.pydantic_output_parser, llm=llm
        )

    def parse_and_retry_if_needed(self, completion: str, prompt_string: str) -> str:
        # If retry_with_error_output_parser is setup, then try parsing with it. Enables 1 retry currently
        if self.retry_with_error_output_parser:
            try:
                parsed_output = self.retry_with_error_output_parser.parse_with_prompt(
                    completion=completion,
                    prompt_value=StringPromptValue(text=prompt_string),
                )
                return parsed_output.json()
            except:
                return FINAL_ERROR_MESSAGE
        # If retry_with_error_output_parser is not setup, then try to parse output directly with no retry
        else:
            try:
                parsed_output = self.pydantic_output_parser.parse(
                    text=completion,
                )
                return parsed_output.json()
            except:
                return FINAL_ERROR_MESSAGE
