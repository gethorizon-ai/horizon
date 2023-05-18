from app import db
from datetime import datetime


class TaskDeploymentLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    prompt_id = db.Column(db.Integer, db.ForeignKey("prompt.id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    input_values = db.Column(db.Text, nullable=False)
    llm_output = db.Column(db.Text, nullable=False)
    inference_latency = db.Column(db.Float, nullable=False)
    inference_data_metric = db.Column(db.String(64), nullable=False)
    prompt_data_length = db.Column(db.Integer, nullable=False)
    output_data_length = db.Column(db.Integer, nullable=False)
    inference_cost = db.Column(db.Float, nullable=False)
    model_name = db.Column(db.String(64), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "timestamp": self.timestamp.isoformat(),
            "prompt_id": self.prompt_id,
            "input_values": self.input_values,
            "llm_output": self.llm_output,
            "inference_latency": self.inference_latency,
            "inference_data_metric": self.inference_data_metric,
            "prompt_data_length": self.prompt_data_length,
            "output_data_length": self.output_data_length,
            "inference_cost": self.inference_cost,
            "model_name": self.model_name,
        }
