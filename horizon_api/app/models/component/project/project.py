from app import db
from datetime import datetime


def generate_user_specific_id(context) -> int:
    """Generate auto-incrementing id per user.

    Retrieves the maximum user-specific task id and returns one more than that. If there are no existing task records, returns 1.

    Args:
        context: SQLAlchemy context object.

    Returns:
        int: one more than the maximum maximum user-specific task id, or 1 if no existing task records.
    """
    user_id = context.get_current_parameters()["user_id"]
    max_user_specific_id = (
        db.session.query(db.func.max(Project.user_specific_id))
        .filter(Project.user_id == user_id)
        .scaler()
    )

    # Return one more than the maximum user-specific id, or 1 if no existing records
    if max_user_specific_id is None:
        return 1
    else:
        return max_user_specific_id + 1


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_specific_id = db.Column(
        db.Integer, nullable=False, default=generate_user_specific_id
    )
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
            "user_specific_id": self.user_specific_id,
            "name": self.name,
        }

    def to_dict_filtered(self):
        # Filter to subset of keys / columns
        filtered_keys = [
            "user_specific_id",
            "name",
        ]
        full_dict = self.to_dict()
        filtered_dict = {key: full_dict[key] for key in filtered_keys}
        return filtered_dict
