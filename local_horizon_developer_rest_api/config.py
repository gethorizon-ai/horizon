import os
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

    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    hostname = os.environ.get('DB_HOSTNAME')
    port = os.environ.get('DB_PORT')
    database_name = os.environ.get('DB_NAME')

    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{username}:{password}@{hostname}:{port}/{database_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AWS_REGION = 'us-west-2'
    COGNITO_POOL_ID = os.environ.get('COGNITO_POOL_ID')
    COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')
    COGNITO_CLIENT_SECRET = os.environ.get('COGNITO_CLIENT_SECRET')
