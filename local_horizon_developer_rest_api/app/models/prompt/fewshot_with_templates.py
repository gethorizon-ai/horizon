from .base import BasePromptTemplate
from langchain.prompts.few_shot_with_templates import FewShotPromptWithTemplates as FewShotWithTemplatesPromptOriginal


class FewshotWithTemplatesPromptTemplate(BasePromptTemplate, FewShotWithTemplatesPromptOriginal):
    pass
