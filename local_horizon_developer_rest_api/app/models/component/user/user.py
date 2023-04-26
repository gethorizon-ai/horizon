from app import db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
from config import Config


def generate_api_key():
    return str(uuid.uuid4())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Changed from username to name
    name = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api_key = db.Column(db.String(36), unique=True,
                        nullable=False, default=generate_api_key)
    projects = db.relationship('Project', backref='user', lazy='dynamic')

    # Initialize the Cognito client
    cognito = boto3.client('cognito-idp',
                           region_name=Config.AWS_REGION)

    # Changed from username to name
    def __init__(self, name, email, password=None, cognito_user=None):
        self.name = name  # Changed from username to name
        self.email = email
        self.api_key = generate_api_key()
        if cognito_user:
            self.id = cognito_user['Username']
        elif password:
            self.create_cognito_user(password)

    def create_cognito_user(self, password):
        response = self.cognito.sign_up(
            ClientId=Config.AWS_COGNITO_APP_CLIENT_ID,
            Username=self.email,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': self.email},
                # Changed from preferred_username to name
                {'Name': 'name', 'Value': self.name}
            ]
        )
        self.id = response['UserSub']

    @classmethod
    def authenticate(cls, email, password):
        try:
            response = cls.cognito.initiate_auth(
                ClientId=Config.AWS_COGNITO_APP_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            return cls.query.filter_by(email=email).first()
        except Exception as e:
            return None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,  # Changed from username to name
            'email': self.email,
            'api_key': self.api_key
        }
