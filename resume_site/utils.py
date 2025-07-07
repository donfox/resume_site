# utils.py

import re
import os
import sys
import io
import contextlib
import logging
logger = logging.getLogger('email')
import traceback
from flask_mail import Message

import smtplib
smtplib.SMTP.debuglevel = 0

# logger = logging.getLogger(__name__)

# Regular expression for validating email addresses
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


# Validate that essential email configuration keys are set
def validate_config(app):
    """Ensure all required mail configs are set and log any missing."""
    required_keys = ["MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_SERVER", "MAIL_PORT"]
    # Check if ant required config keys are missing
    missing_keys = [key for key in required_keys if not app.config.get(key)]

    if missing_keys:
        app.logger.warning(f"Missing mail configuration keys: {', '.join(missing_keys)}")
    else:
        app.logger.info("All required mail configuration keys are present.")


# Log warning if required file does not exist
def ensure_file_exists(file_path):
    """Log a warning if a required file is missing."""
    if not os.path.isfile(file_path):
        app.logger.warning(f"File not found: {file_path}")


def validate_email(email):
    """Validate email format using standard regex."""
    return re.match(EMAIL_REGEX, email) is not None

def send_email(mail, app, recipient, subject, body, attachment_path=None):
    """Send an email with optional attachment using Flask-Mail."""
    try:
        app.logger.info(f"Preparing to send email to {recipient}")

        msg = Message(
            subject,
            sender=app.config.get("MAIL_DEFAULT_SENDER", app.config.get("MAIL_USERNAME")),
            recipients=[recipient]
        )
        msg.body = body

        if attachment_path:
            if not os.path.exists(attachment_path):
                app.logger.warning(f"File not found: {attachment_path}")
            elif os.path.isdir(attachment_path):
                app.logger.warning(f"Attachment path is a directory, skipping: {attachment_path}")
            else:
                with app.open_resource(attachment_path) as f:
                    filename = os.path.basename(attachment_path)
                    msg.attach(filename, "application/octet-stream", f.read())
                app.logger.info(f"Attachment {filename} successfully attached.")

        app.logger.info("Calling mail.send now...")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            mail.send(msg)

        app.logger.info(f"Email sent to {recipient}")
        return True, "Resume has been sent to your email!"

    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")
        tb = traceback.format_exc()
        app.logger.error(f"[FLASK-MAIL ERROR] {e}\n{tb}")
        return False, "Error sending email. Please try again later."