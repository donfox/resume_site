# resume_site/utils.py
from __future__ import annotations

import re
import mimetypes
from pathlib import Path
from typing import Optional, Tuple

from flask import current_app
from flask_mail import Message, Mail

# --- Config validation helpers ---

REQUIRED_MAIL_CONFIG = ("MAIL_DEFAULT_SENDER", "MAIL_SERVER", "MAIL_PORT")

def validate_config(app) -> bool:
    """
    Light sanity check for mail-related config. Logs a friendly message and
    returns True/False (not raising) so app startup never hard-crashes in dev/test.
    """
    missing = [k for k in REQUIRED_MAIL_CONFIG if not app.config.get(k)]
    if missing:
        app.logger.warning(f"⚠️ Missing mail config keys: {', '.join(missing)}")
        return False
    app.logger.info("All required mail configuration keys are present.")
    return True

# --- Email validation ---

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_email(email: str) -> bool:
    """Basic email format check using regex."""
    return bool(email and EMAIL_REGEX.match(email))

# --- Helpers for attachments ---

def _guess_mimetype(path: Path) -> str:
    typ, _ = mimetypes.guess_type(str(path))
    return typ or "application/octet-stream"

# --- Email send wrapper ---

def send_email(
    mail: Mail,
    to_email: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Compose and send an email via Flask-Mail.

    Args (positional, to match existing callers):
        mail: Flask-Mail instance (e.g., current_app.extensions["mail"])
        to_email: Recipient email address
        subject: Email subject
        body: Plain-text body
        attachment_path: Optional filesystem path to a file to attach

    Returns:
        (success, message)
        success=True on send success; otherwise False with a short reason.
    """
    try:
        if mail is None:
            return False, "Mail extension is not initialized"

        default_sender = current_app.config.get("MAIL_DEFAULT_SENDER")
        if not default_sender:
            return False, "MAIL_DEFAULT_SENDER is not configured"

        msg = Message(
            subject=subject,
            sender=default_sender,
            recipients=[to_email],
            body=body,
        )

        if attachment_path:
            p = Path(attachment_path)
            if not p.exists() or not p.is_file():
                current_app.logger.warning(f"Attachment not found: {p}")
            else:
                mime = _guess_mimetype(p)
                with p.open("rb") as fh:
                    msg.attach(
                        filename=p.name,
                        content_type=mime,
                        data=fh.read(),
                    )

        current_app.logger.info(f"📧 Sending email to: {to_email} from {default_sender}")
        mail.send(msg)
        return True, "OK"

    except Exception as e:
        current_app.logger.error("❌ Failed to send email:", exc_info=True)
        return False, f"Error sending email: {e}"