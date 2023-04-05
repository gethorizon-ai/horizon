from .base import BasePromptTemplate
from langchain.prompts.prompt import PromptTemplate as PromptTemplateOriginal


class PromptTemplate(BasePromptTemplate, PromptTemplateOriginal):
    def __init__(self, template: str, input_variables: list):
        super(BasePromptTemplate, self).__init__(
            template=template, input_variables=input_variables)
        super(PromptTemplateOriginal, self).__init__(
            template=template, input_variables=input_variables)

    def to_dict(self):
        return {'template': self.template, 'input_variables': self.input_variables}
