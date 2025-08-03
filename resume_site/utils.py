# utils.py

import os
import re
import traceback
from flask import current_app
from flask_mail import Message
from werkzeug.utils import secure_filename

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_config(app):
    """Ensure all required mail configs are set and log any missing."""
    required_keys = ["MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_SERVER", "MAIL_PORT"]
    missing_keys = [key for key in required_keys if not app.config.get(key)]

    if missing_keys:
        app.logger.warning(f"Missing mail configuration keys: {', '.join(missing_keys)}")
    else:
        app.logger.info("All required mail configuration keys are present.")


def validate_email(email):
    """Validate email format using standard regex."""
    return re.match(EMAIL_REGEX, email) is not None


def send_email(mail, recipient, subject, body_text, attachment_path=None, attachment_name=None):
    try:
        sanitized_recipient = [recipient]
        sanitized_subject = subject.strip()
        sanitized_sender = os.getenv("MAIL_DEFAULT_SENDER") or "you@example.com"

        msg = Message(
            subject=sanitized_subject,
            sender=sanitized_sender,
            recipients=sanitized_recipient,
            body=body_text,
        )

        if attachment_path and os.path.exists(attachment_path):
            name = attachment_name or os.path.basename(attachment_path)
            with open(attachment_path, "rb") as f:
                msg.attach(name, "application/octet-stream", f.read())

        current_app.logger.info(f"📧 Sending email to: {recipient} from {sanitized_sender}")
        mail.send(msg)
        return True, f"✅ Email successfully sent to {recipient}"

    except Exception as e:
        error_message = str(e).strip() or "Unknown Exception"
        tb = traceback.format_exc()
        current_app.logger.error(f"❌ Failed to send email: {e}")
        current_app.logger.error(traceback.format_exc())
        current_app.logger.debug(tb)
        return False, f"Email failed: {error_message}"
