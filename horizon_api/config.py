import os
from kombu.utils.url import safequote


class Config:
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    hostname = os.environ.get("DB_HOSTNAME")
    port = os.environ.get("DB_PORT")
    database_name = "horizon_aditya"  # TODO: os.environ.get("DB_NAME")
    S3_BUCKET = "horizon-api-001"

    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{username}:{password}@{hostname}:{port}/{database_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AWS_REGION = "us-west-2"
    COGNITO_POOL_ID = os.environ.get("COGNITO_POOL_ID")
    COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
    COGNITO_CLIENT_SECRET = os.environ.get("COGNITO_CLIENT_SECRET")

    # Horizon's LLM provider keys
    HORIZON_OPENAI_API_KEY = os.environ.get("HORIZON_OPENAI_API_KEY")
    HORIZON_ANTHROPIC_API_KEY = os.environ.get("HORIZON_ANTHROPIC_API_KEY")

    # Horizon AI test details
    HORIZON_TEST_EMAIL = os.environ.get("HORIZON_TEST_EMAIL")
    HORIZON_TEST_PASSWORD = os.environ.get("HORIZON_TEST_PASSWORD")

    # Connect celery task queue with AWS SQS
    aws_access_key = safequote(os.environ.get("AWS_ACCESS_KEY"))
    aws_secret_key = safequote(os.environ.get("AWS_SECRET_KEY"))
    CELERY_BROKER_URL = f"sqs://{aws_access_key}:{aws_secret_key}@"
    CELERY_TASK_IGNORE_RESULT = True
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "region": AWS_REGION,
        "polling_interval": 15,
        "wait_time_seconds": 15,
    }
    CELERY = {
        "broker_url": CELERY_BROKER_URL,
        "task_ignore_result": CELERY_TASK_IGNORE_RESULT,
        "broker_transport_options": CELERY_BROKER_TRANSPORT_OPTIONS,
    }
