import os
from kombu.utils.url import safequote

# from urllib.parse import quote

# password = "@Mhof98s#fr55"
# encoded_password = quote(password)

# basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     f'mysql+pymysql://ltawfik:{encoded_password}@localhost/horizon_local'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # CORS_HEADERS = 'Content-Type'

    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    hostname = os.environ.get("DB_HOSTNAME")
    port = os.environ.get("DB_PORT")
    database_name = "horizon_aditya"  # os.environ.get("DB_NAME")

    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{username}:{password}@{hostname}:{port}/{database_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AWS_REGION = "us-west-2"
    COGNITO_POOL_ID = os.environ.get("COGNITO_POOL_ID")
    COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
    COGNITO_CLIENT_SECRET = os.environ.get("COGNITO_CLIENT_SECRET")

    # Horizon's OpenAI API key
    HORIZON_OPENAI_API_KEY = os.environ.get("HORIZON_OPENAI_API_KEY")

    # Connect celery task queue with AWS SQS
    aws_access_key = safequote(os.environ.get("AWS_ACCESS_KEY"))
    aws_secret_key = safequote(os.environ.get("AWS_SECRET_KEY"))
    CELERY_BROKER_URL = f"sqs://{aws_access_key}:{aws_secret_key}@"
    CELERY_TASK_IGNORE_RESULT = True
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "region": AWS_REGION,
        "polling_interval": 15,
        "predefined_queues": {
            "my-q": {
                "url": "https://sqs.us-west-2.amazonaws.com/520495742003/TaskGeneration.fifo",
                "access_key_id": aws_access_key,
                "secret_access_key": aws_secret_key,
            }
        },
    }
