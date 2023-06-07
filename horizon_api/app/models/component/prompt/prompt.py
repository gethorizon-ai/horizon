import json
from app import db
from app.models.component.user import User
from app.models.component.project import Project
from app.models.component.task import Task
from app.utilities.dataset_processing import input_variable_naming
from app.models.component.task_deployment_log.task_deployment_log import (
    TaskDeploymentLog,
)
from typing import TYPE_CHECKING
import json


if TYPE_CHECKING:
    from app.models.component.prompt import BasePromptTemplate


def generate_user_specific_id(context) -> int:
    """Generate auto-incrementing id per user.

    Retrieves the maximum user-specific task id and returns one more than that. If there are no existing task records, returns 1.

    Args:
        context: SQLAlchemy context object.

    Returns:
        int: one more than the maximum maximum user-specific task id, or 1 if no existing task records.
    """
    task_id = context.get_current_parameters()["task_id"]

    # Find user
    user = (
        User.query.join(Project, Project.user_id == User.id)
        .join(Task, Task.project_id == Project.id)
        .filter(Task.id == task_id)
        .first()
    )

    # Fetch records corresponding to user
    max_user_specific_id = (
        db.session.query(db.func.max(Prompt.user_specific_id))
        .join(Task, Task.id == Prompt.task_id)
        .join(Project, Project.id == Task.project_id)
        .filter(Project.user_id == user.id)
        .scaler()
    )

    # Return one more than the maximum user-specific id, or 1 if no existing records
    if max_user_specific_id is None:
        return 1
    else:
        return max_user_specific_id + 1


class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_specific_id = db.Column(
        db.Integer, nullable=False, default=generate_user_specific_id
    )
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
    model = db.Column(db.String(200), nullable=True)
    evaluation_job_name = db.Column(db.String(100), nullable=True)
    model_name = db.Column(db.String(100), nullable=True)
    inference_statistics = db.Column(db.String(1000), nullable=True)
    deployment_logs = db.relationship(
        "TaskDeploymentLog",
        backref="prompt",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
        foreign_keys=[TaskDeploymentLog.prompt_id],
        passive_deletes=True,
    )

    def __init__(self, name, task_id, prompt_template: "BasePromptTemplate" = None):
        self.name = name
        self.task_id = task_id
        if prompt_template:
            self.prompt_type = prompt_template.__class__.__name__
            self.template_type = prompt_template.__class__.__name__
            self.template_data = json.dumps(prompt_template.to_dict())

    def to_dict(self):
        return {
            "id": self.id,
            "user_specific_id": self.user_specific_id,
            "name": self.name,
            "task_id": self.task_id,
            "version": self.version,
            "status": self.status,
            "source": self.source,
            "generation_technique": self.generation_technique,
            "prompt_type": self.prompt_type,
            "template_type": self.template_type,
            "template_data": json.loads(self.template_data)
            if self.template_data is not None
            else self.template_data,
            "variables": self.variables,
            "few_shot_template": self.few_shot_template,
            "few_shot_example_selector": self.few_shot_example_selector,
            "model": json.loads(self.model) if self.model is not None else self.model,
            "evaluation_job_name": self.evaluation_job_name,
            "model_name": self.model_name,
            "inference_statistics": json.loads(self.inference_statistics)
            if self.inference_statistics is not None
            else self.inference_statistics,
        }

    def to_dict_filtered(self):
        # Filter to subset of keys / columns
        filtered_keys = [
            "id",
            "user_specific_id",
            "task_id",
            "template_type",
            "template_data",
            "few_shot_example_selector",
            "model",
            "model_name",
            "inference_statistics",
        ]

        # Filter template_data for each prompt template type
        filtered_keys_template_data = {
            "prompt": ["template", "input_variables"],
            "fewshot": ["prefix", "suffix", "input_variables"],
        }

        full_dict = self.to_dict()
        filtered_dict = {key: full_dict[key] for key in filtered_keys}

        # Replace "id" with "user_specific_id"
        filtered_dict["id"] = filtered_dict.pop("user_specific_id")

        if self.template_type is not None:
            # Refine data displayed for template data
            filtered_dict["template_data"] = {
                key: filtered_dict["template_data"][key]
                for key in filtered_keys_template_data[self.template_type]
            }
            # Normalize input variable names
            filtered_dict["template_data"][
                "input_variables"
            ] = input_variable_naming.normalize_input_variable_list(
                filtered_dict["template_data"]["input_variables"]
            )

        return filtered_dict
