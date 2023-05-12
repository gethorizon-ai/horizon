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

PYDANTIC_FORMAT_INSTRUCTIONS = """Only respond with a valid JSON object that conforms to the following JSON schema:
```
{schema}
```"""


class PydanticOutputParser(BaseParser, PydanticOutputParserOriginal):
    """Wrapper around LangChain PydanticOutputParser."""

    def get_format_instructions(self) -> str:
        """Returns output format instructions to append to prompt prefix.

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
        if "properties" in reduced_schema and isinstance(
            reduced_schema["properties"], dict
        ):
            for item, item_details in reduced_schema["properties"].items():
                if isinstance(item_details, dict) and "title" in item_details:
                    del item_details["title"]

        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema)

        return "\n\n" + PYDANTIC_FORMAT_INSTRUCTIONS.format(schema=schema_str).replace(
            "{", "{{"
        ).replace("}", "}}")

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
