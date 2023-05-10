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

PYDANTIC_FORMAT_INSTRUCTIONS = """The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}}}, the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output schema:
```
{schema}
```"""


class PydanticOutputParser(BaseParser, PydanticOutputParserOriginal):
    """Wrapper around LangChain PydanticOutputParser."""

    def get_format_instructions(self) -> str:
        """Returns output format instructions to append to prompt prefix.

        Currently, adds two newlines and removes an unnecessary newline from LangChain's original response.

        Returns:
            str: output format instructions to append to prompt prefix.
        """
        schema = self.pydantic_object.schema()

        # Remove extraneous fields.
        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]
        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema)

        return "\n\n==\nOUTPUT FORMAT:\n\n" + PYDANTIC_FORMAT_INSTRUCTIONS.format(
            schema=schema_str
        ).replace("{", "{{").replace("}", "}}")

    def parse(self, text: str) -> T:
        """Attempts to parse given text according to Pydantic model stored inside.

        Modified implementation of LangChain's parse functionality to handle llm output that may have invalid JSON control characters.

        Args:
            text (str): text to parse into instance of Pydantic class.

        Raises:
            OutputParserException: error in parsing text into Pydantic schema.

        Returns:
            T: instance of Pydantic model class.
        """
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
