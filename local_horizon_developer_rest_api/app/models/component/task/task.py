from app import db
from datetime import datetime
from enum import Enum
import json
import os
from app.models.component.prompt import Prompt
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import event
from sqlalchemy.orm import Session


class TaskStatus(Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(db.Model):
    """Task model."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    objective = db.Column(db.Text, nullable=True)
    task_type = db.Column(db.String(64), nullable=False)
    evaluation_dataset = db.Column(db.String(1000), nullable=True)
    status = db.Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.CREATED)
    create_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    allowed_models = db.Column(db.String(200), nullable=False)
    prompts = db.relationship(
        "Prompt",
        backref="task",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
        foreign_keys=[Prompt.task_id],
        passive_deletes=True,
    )
    active_prompt_id = db.Column(
        db.Integer,
        db.ForeignKey("prompt.id", use_alter=True, ondelete="SET NULL"),
        nullable=True,
    )
    evaluation_statistics = db.Column(db.String(1000), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "objective": self.objective,
            "task_type": self.task_type,
            "evaluation_dataset": self.evaluation_dataset,
            "status": self.status,
            "create_timestamp": datetime.isoformat(self.create_timestamp),
            "project_id": self.project_id,
            "allowed_models": json.loads(self.allowed_models)
            if (self.allowed_models != None and self.allowed_models != "")
            else self.allowed_models,
            "active_prompt_id": self.active_prompt_id,
            "prompts": [prompt.to_dict() for prompt in self.prompts.all()],
            "evaluation_statistics": json.loads(self.evaluation_statistics)
            if self.evaluation_statistics != None
            else self.evaluation_statistics,
        }

    def to_dict_filtered(self):
        # Filter to subset of keys / columns
        filtered_keys = [
            "id",
            "name",
            "objective",
            "project_id",
            "allowed_models",
            "active_prompt_id",
            "evaluation_statistics",
        ]
        full_dict = self.to_dict()
        filtered_dict = {key: full_dict[key] for key in filtered_keys}

        # Add filtered values of prompts
        filtered_dict["prompts"] = [
            prompt.to_dict_filtered() for prompt in self.prompts.all()
        ]

        return filtered_dict


@event.listens_for(Task, "before_delete")
def _remove_evaluation_dataset_and_active_prompt_id(mapper, connection, target):
    # Delete evaluation dataset, if it exists
    if target.evaluation_dataset != None:
        os.remove(path=target.evaluation_dataset)
        target.evaluation_dataset = None

    # Set active_prompt_id to None
    if target.active_prompt_id != None:
        target.active_prompt_id = None

    # Create a new session for the delete operation
    session = Session(bind=connection)
    session.add(target)
    session.commit()
