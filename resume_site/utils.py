# utils.py

import re
import os
import logging
import traceback
from flask import current_app
from flask_mail import Message

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


from flask import current_app
from flask_mail import Message
import logging

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

        mail.send(msg)
        return True, f"✅ Email successfully sent to {recipient}"
    except Exception as e:
        current_app.logger.error(f"❌ Failed to send email: {e}")
        return False, str(e)

# def send_email(mail, app, recipient, subject, body, attachment_path=None):
#     """Send an email with optional attachment using Flask-Mail."""
#     try:
#         app.logger.info(f"Preparing to send email to {recipient}")

#         msg = Message(
#             subject=subject.strip(),
#             sender=(app.config.get("MAIL_DEFAULT_SENDER") or app.config.get("MAIL_USERNAME") or "").strip(),
#             recipients=[recipient],
#             body=body
#         )

#         app.logger.info(f"Sanitized sender: {msg.sender}")
#         app.logger.info(f"Sanitized recipient(s): {msg.recipients}")
#         app.logger.info(f"Sanitized subject: {msg.subject}")

#         if attachment_path:
#             if not os.path.exists(attachment_path):
#                 app.logger.warning(f"File not found: {attachment_path}")
#             elif os.path.isdir(attachment_path):
#                 app.logger.warning(f"Attachment path is a directory, skipping: {attachment_path}")
#             else:
#                 with app.open_resource(attachment_path) as f:
#                     filename = os.path.basename(attachment_path)
#                     msg.attach(filename, "application/octet-stream", f.read())
#                 app.logger.info(f"Attachment added: {filename}")

#         app.logger.info(f"Sending email to: {recipient} with subject: {subject}")
#         mail.send(msg)
#         app.logger.info(f"✅ Email successfully sent to {recipient}")

#         return True, "Resume has been sent to your email!"

#     except Exception as e:
#         tb = traceback.format_exc()
#         app.logger.error(f"❌ Failed to send email to {recipient}")
#         app.logger.error(f"[FLASK-MAIL ERROR] {e}\n{tb}")
#         return False, "Error sending email. Please try again later."
