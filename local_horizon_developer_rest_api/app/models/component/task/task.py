from app import db
from datetime import datetime
from enum import Enum
from app.models.component.prompt import Prompt
from sqlalchemy import Enum as SQLEnum


# class TaskStatus(Enum):
#     CREATED = 'created'
#     IN_PROGRESS = 'in_progress'
#     COMPLETED = 'completed'


class Task(db.Model):
    """Task model."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    task_type = db.Column(db.String(64), nullable=False)
    evaluation_dataset = db.Column(db.String(100), nullable=True)
    # status = db.Column(SQLEnum(TaskStatus), nullable=False,
    #                    default=TaskStatus.CREATED)
    status = db.Column(db.String(64), nullable=False, default='created')
    create_timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), nullable=False)
    prompts = db.relationship(
        'Prompt', backref='task', lazy='dynamic', cascade='all, delete, delete-orphan', foreign_keys=[Prompt.task_id], passive_deletes=True)
    active_prompt_id = db.Column(
        db.Integer, db.ForeignKey('prompt.id', use_alter=True), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'task_type': self.task_type,
            'evaluation_dataset': self.evaluation_dataset,
            # 'status': self.status.value,  # Convert the TaskStatus object to a string
            'status': self.status,
            'create_timestamp': datetime.isoformat(self.create_timestamp),
            'project_id': self.project_id,
            'active_prompt_id': self.active_prompt_id,
            'prompts': [prompt.to_dict() for prompt in self.prompts.all()]
        }
