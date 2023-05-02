from app import db
import uuid
import hashlib


def generate_api_key():
    return str(uuid.uuid4())


class User(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    api_key_hash = db.Column(db.String(128), unique=True, nullable=False)
    projects = db.relationship("Project", backref="user", lazy="dynamic")

    def __init__(self, id):
        self.id = id
        api_key = generate_api_key()
        self.api_key_hash = hashlib.sha256(api_key.encode("UTF-8")).hexdigest()

    def generate_new_api_key(self):
        api_key = generate_api_key()
        self.api_key_hash = hashlib.sha256(api_key.encode("UTF-8")).hexdigest()
        return api_key

    def check_api_key(self, api_key):
        api_key_hash = hashlib.sha256(api_key.encode("UTF-8")).hexdigest()
        return self.api_key_hash == api_key_hash
