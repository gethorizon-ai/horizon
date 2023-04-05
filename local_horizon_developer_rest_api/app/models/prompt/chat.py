from .base import BasePromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate as ChatPromptTemplateOriginal,
    ChatMessagePromptTemplate as ChatMessagePromptTemplateOriginal,
    HumanMessagePromptTemplate as HumanMessagePromptTemplateOriginal,
    AIMessagePromptTemplate as AIMessagePromptTemplateOriginal,
    SystemMessagePromptTemplate as SystemMessagePromptTemplateOriginal,
    MessagesPlaceholder as MessagesPlaceholderOriginal,
    ChatPromptValue as ChatPromptValueOriginal,
)


class ChatPromptTemplate(BasePromptTemplate, ChatPromptTemplateOriginal):
    pass


class ChatMessagePromptTemplate(BasePromptTemplate, ChatMessagePromptTemplateOriginal):
    pass


class HumanMessagePromptTemplate(BasePromptTemplate, HumanMessagePromptTemplateOriginal):
    pass


class AIMessagePromptTemplate(BasePromptTemplate, AIMessagePromptTemplateOriginal):
    pass


class SystemMessagePromptTemplate(BasePromptTemplate, SystemMessagePromptTemplateOriginal):
    pass


class MessagesPlaceholder(BasePromptTemplate, MessagesPlaceholderOriginal):
    pass


class ChatPromptValue(BasePromptTemplate, ChatPromptValueOriginal):
    pass
