from app import db
from datetime import datetime
import base64


from app import db
from datetime import datetime
import base64


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(64), nullable=False, default="created")
    create_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.String(64), db.ForeignKey("user.id"), nullable=False)
    tasks = db.relationship(
        "Task", backref="project", lazy="dynamic", cascade="all,delete"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "create_timestamp": datetime.isoformat(self.create_timestamp),
            "user_id": self.user_id,
        }
