# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from .extensions import db


# Model for tracking resume requests
class EmailRequest(db.Model):
    __tablename__ = "EmailRequest"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128))
    ip_address = db.Column(db.String(64))
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )  # Timestamp recorded in UTC

    def __repr__(self):
        return f"<EmailRequest {self.name}, {self.email}>"


# Model for storing user-submitted contact messages
class UserMessage(db.Model):
    __tablename__ = "UserMessage"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    subject = db.Column(db.String(256))  # Optional subject line
    message = db.Column(db.Text)  # Full message content
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )  # Timestamp recorded in UTC

    def __repr__(self):
        return f"<UserMessage from {self.name}>"
