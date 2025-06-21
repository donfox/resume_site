# utils.py

import re
import os
import sys
import io
import logging
from flask_mail import Message

logger = logging.getLogger(__name__)

# Regular expression for validating email addresses
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


# Validate that essential email configuration keys are set
def validate_config(app):
    """Ensure all required mail configs are set and log any missing."""
    required_keys = ["MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_SERVER", "MAIL_PORT"]
    # Check if ant required config keys are missing
    missing_keys = [key for key in required_keys if not app.config.get(key)]

    if missing_keys:
        logger.warning(f"Missing mail configuration keys: {', '.join(missing_keys)}")
    else:
        logger.info("All required mail configuration keys are present.")


# Log warning if required file does not exist
def ensure_file_exists(file_path):
    """Log a warning if a required file is missing."""
    if not os.path.isfile(file_path):
        logger.warning(f"File not found: {file_path}")


def validate_email(email):
    """Validate email format using standard regex."""
    return re.match(EMAIL_REGEX, email) is not None


def send_email(mail, app, recipient, subject, body, attachment_path=None):
    """Send an email with optional attachment."""
    try:
        import smtplib
        smtplib.SMTP.debuglevel = 0

        msg = Message(
            subject,
            sender=app.config["MAIL_USERNAME"],
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

        # 🔇 Fully suppress stdout/stderr during mail.send()
        stdout_backup = sys.stdout
        stderr_backup = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            mail.send(msg)
        finally:
            sys.stdout = stdout_backup
            sys.stderr = stderr_backup

        logger.info(f"Email sent to {recipient}")
        return True, "Resume has been sent to your email!"
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
        return False, "Error sending email. Please try again later."
        