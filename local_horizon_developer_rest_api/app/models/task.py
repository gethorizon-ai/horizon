from app import db
from datetime import datetime


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    task_type = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(64), nullable=False, default='created')
    create_timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), nullable=False)
    prompts = db.relationship(
        'Prompt', backref='project', lazy='dynamic', cascade='all,delete')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'task_type': self.task_type,
            'status': self.status,
            'create_timestamp': datetime.isoformat(self.create_timestamp),
            'project_id': self.project_id,
            'prompts': [prompt.to_dict() for prompt in self.prompts.all()]
        }
