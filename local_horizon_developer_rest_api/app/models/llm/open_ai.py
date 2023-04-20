from langchain.llms import OpenAI as OpenAIOriginal
from langchain.chat_models import ChatOpenAI as ChatOpenAIOriginal
from .base import BaseLLM


class OpenAI(BaseLLM, OpenAIOriginal):
    pass


class ChatOpenAI(BaseLLM, ChatOpenAIOriginal):
    pass
