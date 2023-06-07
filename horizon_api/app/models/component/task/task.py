from app import db
from datetime import datetime
from enum import Enum
import json
import os
from app.models.component import User, Project
from app.models.component.prompt import Prompt
from app.models.component.task_deployment_log.task_deployment_log import (
    TaskDeploymentLog,
)
from app.models.vector_stores.pinecone import Pinecone
from app.utilities.S3.s3_util import delete_file_from_s3
from app.utilities.vector_db import vector_db
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import event


class TaskStatus(Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


def generate_user_specific_id(context) -> int:
    """Generate auto-incrementing id per user.

    Retrieves the maximum user-specific task id and returns one more than that. If there are no existing task records, returns 1.

    Args:
        context: SQLAlchemy context object.

    Returns:
        int: one more than the maximum maximum user-specific task id, or 1 if no existing task records.
    """
    project_id = context.get_current_parameters()["project_id"]

    # Find user
    user = (
        User.query.join(Project, Project.user_id == User.id)
        .filter(Project.id == project_id)
        .first()
    )

    # Fetch max value of user-specific task id
    max_user_specific_id = (
        db.session.query(db.func.max(Task.user_specific_id))
        .join(Project, Project.id == Task.project_id)
        .filter(Project.user_id == user.id)
        .scaler()
    )

    # Return one more than the maximum user-specific id, or 1 if no existing records
    if max_user_specific_id is None:
        return 1
    else:
        return max_user_specific_id + 1


class Task(db.Model):
    """Task model."""

    id = db.Column(db.Integer, primary_key=True)
    user_specific_id = db.Column(
        db.Integer, nullable=False, default=generate_user_specific_id
    )
    name = db.Column(db.String(64), nullable=False)
    objective = db.Column(db.Text, nullable=True)
    task_type = db.Column(db.String(64), nullable=False)
    evaluation_dataset = db.Column(db.Text, nullable=True)
    vector_db_metadata = db.Column(db.Text, nullable=True)
    output_schema = db.Column(db.Text, nullable=True)
    pydantic_model = db.Column(db.Text, nullable=True)
    status = db.Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.CREATED)
    create_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    allowed_models = db.Column(db.String(200), nullable=False)
    active_prompt_id = db.Column(
        db.Integer,
        db.ForeignKey("prompt.id", use_alter=True, ondelete="SET NULL"),
        nullable=True,
    )
    evaluation_statistics = db.Column(db.String(1000), nullable=True)
    deployment_logs = db.relationship(
        "TaskDeploymentLog",
        backref="task",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
        foreign_keys=[TaskDeploymentLog.task_id],
        passive_deletes=True,
    )
    prompts = db.relationship(
        "Prompt",
        backref="task",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
        foreign_keys=[Prompt.task_id],
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_specific_id": self.user_specific_id,
            "name": self.name,
            "objective": self.objective,
            "task_type": self.task_type,
            "evaluation_dataset": self.evaluation_dataset,
            "vector_db_metadata": self.vector_db_metadata,
            "output_schema": os.path.basename(self.output_schema)
            if (self.output_schema is not None)
            else "Undefined",
            "pydantic_model": os.path.basename(self.pydantic_model)
            if (self.pydantic_model is not None)
            else "Undefined",
            "status": self.status,
            "create_timestamp": datetime.isoformat(self.create_timestamp),
            "project_id": self.project_id,
            "allowed_models": json.loads(self.allowed_models)
            if (self.allowed_models is not None and self.allowed_models != "")
            else self.allowed_models,
            "active_prompt_id": self.active_prompt_id,
            "prompts": [prompt.to_dict() for prompt in self.prompts.all()],
            "evaluation_statistics": json.loads(self.evaluation_statistics)
            if self.evaluation_statistics is not None
            else self.evaluation_statistics,
        }

    def to_dict_filtered(self):
        # Filter to subset of keys / columns
        filtered_keys = [
            "user_specific_id",
            "name",
            "objective",
            "output_schema",
            "project_id",
            "allowed_models",
            "active_prompt_id",
            "evaluation_statistics",
        ]
        full_dict = self.to_dict()
        filtered_dict = {key: full_dict[key] for key in filtered_keys}

        # Update project id to user-specific id
        project = Project.query.get(filtered_dict["project_id"])
        filtered_dict["project_id"] = project.user_specific_id

        # Add filtered values of prompts
        filtered_dict["prompts"] = [
            prompt.to_dict_filtered() for prompt in self.prompts.all()
        ]

        return filtered_dict

    def store_vector_db_metadata(self, vector_db: Pinecone) -> None:
        vector_db_metadata = {
            "namespace": vector_db.get_namespace(),
            "input_variables": vector_db.get_input_variables(),
            "num_unique_data": vector_db.get_num_unique_data(),
        }
        self.vector_db_metadata = json.dumps(vector_db_metadata)
        db.session.commit()


@event.listens_for(Task, "before_delete")
def _clean_up_and_remove_dependencies(mapper, connection, target):
    # Delete raw evaluation dataset from S3, if it exists
    if target.evaluation_dataset is not None:
        try:
            delete_file_from_s3(target.evaluation_dataset)
        except:
            pass
        target.evaluation_dataset = None

    # Delete evaluation dataset from vector db, if it exists
    if target.vector_db_metadata is not None:
        try:
            vector_db.delete_vector_db(json.loads(target.vector_db_metadata))
        except:
            pass
        target.vector_db_metadata = None

    # Delete output schema from S3, if it exists
    if target.output_schema is not None:
        try:
            delete_file_from_s3(target.output_schema)
        except:
            pass
        target.output_schema = None

    # Delete pydantic model from S3, if it exists
    if target.pydantic_model is not None:
        try:
            delete_file_from_s3(target.pydantic_model)
        except:
            pass
        target.pydantic_model = None

    # Set active_prompt_id to None
    if target.active_prompt_id is not None:
        target.active_prompt_id = None

    # Commit changes
    connection.execute(
        target.__table__.update()
        .where(target.__table__.c.id == target.id)
        .values(
            evaluation_dataset=target.evaluation_dataset,
            vector_db_metadata=target.vector_db_metadata,
            output_schema=target.output_schema,
            pydantic_model=target.pydantic_model,
            active_prompt_id=target.active_prompt_id,
        )
    )
    connection.execute("commit")
