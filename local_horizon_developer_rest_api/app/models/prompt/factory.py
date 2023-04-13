from typing import Type, Dict
from .base import BasePromptTemplate
from .chat import (
    ChatPromptTemplate,
    ChatMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    ChatPromptValue,
)
from .fewshot import FewshotPromptTemplate
from .fewshot_with_templates import FewshotWithTemplatesPromptTemplate
from .prompt import PromptTemplate


class PromptTemplateFactory:
    prompt_template_classes = {
        "chat": ChatPromptTemplate,
        "fewshot": FewshotPromptTemplate,
        "fewshot_with_templates": FewshotWithTemplatesPromptTemplate,
        "prompt": PromptTemplate,
        "chat_message": ChatMessagePromptTemplate,
        "human_message": HumanMessagePromptTemplate,
        "ai_message": AIMessagePromptTemplate,
        "system_message": SystemMessagePromptTemplate,
        "messages_placeholder": MessagesPlaceholder,
        "chat_prompt_value": ChatPromptValue,
    }

    @staticmethod
    def create_prompt_template(template_type: str, **kwargs) -> BasePromptTemplate:
        if template_type not in PromptTemplateFactory.prompt_template_classes:
            raise ValueError(f"Invalid template_type: {template_type}")

        return PromptTemplateFactory.prompt_template_classes[template_type](**kwargs)
