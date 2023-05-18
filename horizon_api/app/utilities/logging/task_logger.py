from app import db
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
        input_values: dict,
        llm_output: str,
        inference_latency: float,
        prompt_data_length: int,
        output_data_length: int,
        model_name: str,
        inference_cost: float,
    ):
        # Prepare log entry
        log_entry = TaskDeploymentLog()

        log_entry.task_id = task_id
        log_entry.prompt_id = prompt_id
        log_entry.timestamp = timestamp
        log_entry.input_values = str(input_values)
        log_entry.llm_output = llm_output
        log_entry.inference_latency = inference_latency
        log_entry.inference_data_metric = "seconds"
        log_entry.inference_cost = inference_cost
        log_entry.prompt_data_length = prompt_data_length
        log_entry.output_data_length = output_data_length
        log_entry.model_name = model_name

        db.session.add(log_entry)
        db.session.commit()

        return log_entry

    def get_logs(self, task_id=None):
        if task_id:
            logs = TaskDeploymentLog.query.filter_by(task_id=task_id).all()
        else:
            logs = TaskDeploymentLog.query.all()

        df = pd.DataFrame([log.to_dict() for log in logs])
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Prepare a unique log file name
        if task_id:
            log_file_name = f"deployment_logs/{task_id}/{datetime.datetime.now().strftime('%Y/%m/%d/%H%M%SZ')}/deployment_logs_{task_id}.csv"
        else:
            log_file_name = f"deployment_logs/all/{datetime.datetime.now().strftime('%Y/%m/%d/%H%M%SZ')}/deployment_logs.csv"

        upload_file_to_s3(file=csv_buffer, key=log_file_name)

        return log_file_name

    def clear_logs():
        TaskDeploymentLog.query.delete()
        db.session.commit()
