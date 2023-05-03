import os


class Config:

    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    hostname = os.environ.get("DB_HOSTNAME")
    port = os.environ.get("DB_PORT")
    database_name = os.environ.get("DB_NAME")

    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{username}:{password}@{hostname}:{port}/{database_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AWS_REGION = "us-west-2"
    COGNITO_POOL_ID = os.environ.get("COGNITO_POOL_ID")
    COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
    COGNITO_CLIENT_SECRET = os.environ.get("COGNITO_CLIENT_SECRET")

    # Horizon's OpenAI API key
    HORIZON_OPENAI_API_KEY = os.environ.get("HORIZON_OPENAI_API_KEY")
