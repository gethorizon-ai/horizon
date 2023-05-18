"""Example Pydantic data model to test output schema functionality."""

from pydantic import BaseModel, Field, validator


# Define your desired data structure.
class OutputSchema(BaseModel):
    title: str = Field(description="title of the page")
    content: str = Field(description="content of the page")
