from app import db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


def generate_api_key():
    return str(uuid.uuid4())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    api_key = db.Column(db.String(36), unique=True,
                        nullable=False, default=generate_api_key)
    projects = db.relationship('Project', backref='user', lazy='dynamic')

    def __init__(self, username, email, password=None, hashed_password=None):
        self.username = username
        self.email = email
        if hashed_password:
            self.password_hash = hashed_password
        elif password:
            self.set_password(password)
        self.api_key = generate_api_key()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'api_key': self.api_key
        }
