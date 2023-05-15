from .base import BaseEmbeddings
from langchain.embeddings import OpenAIEmbeddings as OpenAIEmbeddingsOriginal
import openai
from pydantic import root_validator
from typing import (
    Any,
    Dict,
    Literal,
    Set,
    Union,
)


class OpenAIEmbeddings(OpenAIEmbeddingsOriginal):
    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        values = super().validate_environment(values)
        return values

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # def embed_documents(self, *args: Any, **kwargs: Any) -> Any:
    #     # Reset OpenAI API key in case it was changed by other processes (e.g., llm inference calls)
    #     openai.api_key = self.openai_api_key
    #     return super(OpenAIEmbeddingsOriginal, self).embed_documents(*args, **kwargs)

    # def embed_query(self, *args: Any, **kwargs: Any) -> Any:
    #     # Reset OpenAI API key in case it was changed by other processes (e.g., llm inference calls)
    #     openai.api_key = self.openai_api_key
    #     return super(OpenAIEmbeddingsOriginal, self).embed_query(*args, **kwargs)
    pass
