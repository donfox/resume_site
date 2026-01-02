# models.py

# resume_site/models.py
from datetime import datetime, timezone
from .extensions import db


# Model for tracking resume requests
class EmailRequest(db.Model):
    """
    Tracks individual requests for a resume download or email.
    Works identically on SQLite and PostgreSQL.
    """

    __tablename__ = "email_request"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128))
    ip_address = db.Column(db.String(64))
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )  # UTC timestamp

    def __repr__(self):
        return f"<EmailRequest {self.name}, {self.email}>"


# Model for storing user-submitted contact messages
class UserMessage(db.Model):
    """
    Stores messages submitted through a contact form.
    Compatible with both SQLite and PostgreSQL.
    """

    __tablename__ = "user_message"  # lowercase

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    subject = db.Column(db.String(256))  # optional subject line
    message = db.Column(db.Text, nullable=False)  # full message content
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return f"<UserMessage from {self.name}>"
