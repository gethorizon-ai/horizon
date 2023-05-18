from app import db
from sqlalchemy.exc import IntegrityError
from app.models.component.task_deployment_log.task_deployment_log import (
    TaskDeploymentLog,
)
from app.utilities.S3.s3_util import upload_file_to_s3
from datetime import datetime
import pandas as pd
from io import BytesIO


class TaskLogger:
    def __init__(self):
        self.log_data = []

    def log_deployment(
        self,
        task_id: str,
        prompt_id: int,
        timestamp: datetime,
        model_name: str,
        input_values: dict,
        llm_completion: str,
        inference_latency: float,
        data_unit: str,
        prompt_data_length: int,
        completion_data_length: int,
        prompt_cost: float,
        completion_cost: float,
        total_inference_cost: float,
    ):
        # Prepare log entry
        log_entry = TaskDeploymentLog()

        log_entry.task_id = task_id
        log_entry.prompt_id = prompt_id
        log_entry.timestamp = timestamp
        log_entry.model_name = model_name
        log_entry.input_values = str(input_values)
        log_entry.llm_completion = llm_completion
        log_entry.inference_latency = inference_latency
        log_entry.data_unit = data_unit
        log_entry.prompt_data_length = prompt_data_length
        log_entry.completion_data_length = completion_data_length
        log_entry.prompt_cost = prompt_cost
        log_entry.completion_cost = completion_cost
        log_entry.total_inference_cost = total_inference_cost

        db.session.add(log_entry)
        db.session.commit()

        return log_entry

    def get_logs(self, task_id=None):
        if task_id:
            logs = TaskDeploymentLog.query.filter_by(task_id=task_id).all()
        else:
            logs = TaskDeploymentLog.query.all()

        if logs == None:
            return None

        df = pd.DataFrame([log.to_dict() for log in logs])
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Prepare a unique log file name
        if task_id:
            log_file_name = f"deployment_logs/{task_id}/{datetime.now().strftime('%Y/%m/%d/%H%M%SZ')}/deployment_logs_{task_id}.csv"
        else:
            log_file_name = f"deployment_logs/all_tasks/{datetime.now().strftime('%Y/%m/%d/%H%M%SZ')}/deployment_logs.csv"

        upload_file_to_s3(file=csv_buffer, key=log_file_name)

        return log_file_name

    def clear_logs():
        TaskDeploymentLog.query.delete()
        db.session.commit()
