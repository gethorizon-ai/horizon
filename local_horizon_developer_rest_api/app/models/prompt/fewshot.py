from .base import BasePromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate as FewShotPromptOriginal


class FewshotPromptTemplate(BasePromptTemplate, FewShotPromptOriginal):
    pass
