# resume_site/utils.py
from __future__ import annotations

import re
import mimetypes
import socket
import smtplib
import time
from pathlib import Path
from typing import Optional, Tuple

from flask import current_app
from flask_mail import Message, Mail

# --- Config validation helpers ---

REQUIRED_MAIL_CONFIG = ("MAIL_DEFAULT_SENDER", "MAIL_SERVER", "MAIL_PORT")


def validate_config(app) -> None:
    """
    Light sanity check for mail-related config. Logs a friendly message.
    Does not raise so app startup never hard-crashes in dev/test.
    """
    missing = [k for k in REQUIRED_MAIL_CONFIG if not app.config.get(k)]
    if missing:
        app.logger.warning(f"⚠️ Missing mail config keys: {', '.join(missing)}")
    else:
        app.logger.info("All required mail configuration keys are present.")


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

        required = {
            "MAIL_DEFAULT_SENDER": current_app.config.get("MAIL_DEFAULT_SENDER"),
            "MAIL_SERVER": current_app.config.get("MAIL_SERVER"),
            "MAIL_PORT": current_app.config.get("MAIL_PORT"),
            "MAIL_USERNAME": current_app.config.get("MAIL_USERNAME"),
            "MAIL_PASSWORD": current_app.config.get("MAIL_PASSWORD"),
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            return False, f"Missing mail config: {', '.join(missing)}"

        default_sender = required["MAIL_DEFAULT_SENDER"]

        msg = Message(
            subject=subject,
            sender=default_sender,
            recipients=[to_email],
            body=body,
        )

        # TODO: SPAM ISSUE - Update BREVO_MAIL_DEFAULT_SENDER in .env
        # Currently sending from donfox1@mac.com through Brevo causes spam filtering
        # because Apple's domain doesn't authorize Brevo's servers (SPF/DKIM failure).
        # FIX: Use a Brevo-verified sender address from your Brevo account dashboard.
        # Go to: https://app.brevo.com → Settings → Senders
        # Then update .env: BREVO_MAIL_DEFAULT_SENDER=your-verified-email@yourdomain.com

        # Add reply-to to make it look more legitimate
        msg.reply_to = "donfox1@mac.com"

        # Add custom headers to reduce spam score
        msg.extra_headers = {
            "X-Mailer": "Flask-Mail",
            "X-Priority": "3",
        }

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

        started = time.monotonic()
        current_app.logger.info(
            "📧 Sending email to: %s from %s via %s:%s (timeout=%ss)",
            to_email,
            default_sender,
            current_app.config.get("MAIL_SERVER"),
            current_app.config.get("MAIL_PORT"),
            current_app.config.get("MAIL_TIMEOUT"),
        )
        mail.send(msg)
        elapsed = time.monotonic() - started
        current_app.logger.info("✅ Email send completed in %.2fs", elapsed)
        return True, "OK"

    except (socket.timeout, TimeoutError):
        current_app.logger.error("❌ SMTP timeout while sending email", exc_info=True)
        return False, "SMTP connection timed out"
    except smtplib.SMTPServerDisconnected as e:
        current_app.logger.error("❌ SMTP server disconnected", exc_info=True)
        return False, f"SMTP disconnected: {e}"
    except Exception as e:
        current_app.logger.error("❌ Failed to send email:", exc_info=True)
        return False, f"Error sending email: {e}"
