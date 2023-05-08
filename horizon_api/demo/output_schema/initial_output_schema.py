"""Example Pydantic data model to test output schema functionality."""

from pydantic import BaseModel, Field, validator


# Define your desired data structure.
class User(BaseModel):
    id: int = Field(description="id of the individual")
    name: str = Field(description="name of the individual")


class OutputSchema(BaseModel):
    id: int = Field(description="id of the post")
    title: str = Field(description="title of the post")
    content: str = Field(description="content of the post")
    author: User = Field(description="user who wrote the post")
