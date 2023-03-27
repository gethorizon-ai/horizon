from app import db


class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    version = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(100), nullable=True)
    source = db.Column(db.String(100), nullable=True)
    generation_technique = db.Column(db.String(100), nullable=True)
    prompt_type = db.Column(db.String(100), nullable=True)
    template = db.Column(db.String(100), nullable=True)
    variables = db.Column(db.String(100), nullable=True)
    few_shot_template = db.Column(db.String(100), nullable=True)
    few_shot_example_selector = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    evaluation_job_name = db.Column(db.String(100), nullable=True)

    def __init__(self, name, task_id):
        self.name = name
        self.task_id = task_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'task_id': self.task_id,
            'version': self.version,
            'status': self.status,
            'source': self.source,
            'generation_technique': self.generation_technique,
            'prompt_type': self.prompt_type,
            'template': self.template,
            'variables': self.variables,
            'few_shot_template': self.few_shot_template,
            'few_shot_example_selector': self.few_shot_example_selector,
            'model': self.model,
            'evaluation_job_name': self.evaluation_job_name
        }
