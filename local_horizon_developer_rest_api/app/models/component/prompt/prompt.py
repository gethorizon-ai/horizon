import json
from app import db
from typing import TYPE_CHECKING
from app.models.prompt.factory import PromptTemplateFactory


if TYPE_CHECKING:
    from app.models.component.prompt import BasePromptTemplate


class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    task_id = db.Column(
        db.Integer, db.ForeignKey("task.id", ondelete="CASCADE"), nullable=False
    )
    version = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    source = db.Column(db.String(50), nullable=True)
    generation_technique = db.Column(db.String(50), nullable=True)
    prompt_type = db.Column(db.String(100), nullable=True)
    template_type = db.Column(db.String(100), nullable=True)
    template_data = db.Column(db.String(4000), nullable=True)
    variables = db.Column(db.String(100), nullable=True)
    few_shot_template = db.Column(db.String(100), nullable=True)
    few_shot_example_selector = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    evaluation_job_name = db.Column(db.String(100), nullable=True)
    model_name = db.Column(db.String(100), nullable=True)

    def __init__(self, name, task_id, prompt_template: "BasePromptTemplate" = None):
        self.name = name
        self.task_id = task_id
        if prompt_template:
            self.prompt_type = prompt_template.__class__.__name__
            self.template_type = prompt_template.__class__.__name__
            self.template_data = json.dumps(prompt_template.to_dict())

    def to_dict(self):
        prompt_dict = {
            "id": self.id,
            "name": self.name,
            "task_id": self.task_id,
            "version": self.version,
            "status": self.status,
            "source": self.source,
            "generation_technique": self.generation_technique,
            "prompt_type": self.prompt_type,
            "template_type": self.template_type,
            # "template_data": self.get_template_object(),
            "template_data": self.template_data,
            "variables": self.variables,
            "few_shot_template": self.few_shot_template,
            "few_shot_example_selector": self.few_shot_example_selector,
            "model": self.model,
            "evaluation_job_name": self.evaluation_job_name,
            "model_name": self.model_name,
        }
        return prompt_dict

    # def get_template_object(self) -> "BasePromptTemplate":
    #     if self.template_data:
    #         template_dict = json.loads(self.template_data)
    #         return PromptTemplateFactory.create_prompt_template(
    #             self.template_type, **template_dict
    #         )
    #     return None
