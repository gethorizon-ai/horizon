from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from .base import BaseLLM


class OpenAI(BaseLLM, OpenAI):
    pass


class ChatOpenAI(BaseLLM, ChatOpenAI):
    pass
