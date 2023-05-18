from app import db
from datetime import datetime


class TaskDeploymentLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    prompt_id = db.Column(db.Integer, db.ForeignKey("prompt.id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    model_name = db.Column(db.String(64), nullable=False)
    input_values = db.Column(db.Text, nullable=False)
    llm_completion = db.Column(db.Text, nullable=False)
    inference_latency = db.Column(db.Float, nullable=False)
    data_unit = db.Column(db.String(64), nullable=False)
    prompt_data_length = db.Column(db.Integer, nullable=False)
    completion_data_length = db.Column(db.Integer, nullable=False)
    prompt_cost = db.Column(db.Float, nullable=False)
    completion_cost = db.Column(db.Float, nullable=False)
    total_inference_cost = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "prompt_id": self.prompt_id,
            "timestamp": self.timestamp.isoformat(),
            "model_name": self.model_name,
            "input_values": self.input_values,
            "llm_completion": self.llm_completion,
            "inference_latency": self.inference_latency,
            "data_unit": self.data_unit,
            "prompt_data_length": self.prompt_data_length,
            "completion_data_length": self.completion_data_length,
            "prompt_cost": self.prompt_cost,
            "completion_cost": self.completion_cost,
            "total_inference_cost": self.total_inference_cost,
        }
