# resume_site/utils.py
from __future__ import annotations

import re
import mimetypes
import socket
import smtplib
import time
import base64
from pathlib import Path
from typing import Optional, Tuple

import requests
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
    Send email via Brevo HTTP API (preferred) with Flask-Mail SMTP fallback.
    Uses BREVO_API_KEY env var when available; otherwise falls back to SMTP.
    """
    api_key = current_app.config.get("BREVO_API_KEY")
    if api_key:
        return _send_via_brevo_api(api_key, to_email, subject, body, attachment_path)
    return _send_via_smtp(mail, to_email, subject, body, attachment_path)


def _send_via_brevo_api(
    api_key: str,
    to_email: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """Call Brevo transactional email REST API (HTTPS/443 — works on all platforms)."""
    default_sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    if not default_sender:
        return False, "MAIL_DEFAULT_SENDER is not configured"

    payload: dict = {
        "sender": {"email": default_sender},
        "to": [{"email": to_email}],
        "replyTo": {"email": "donfox1@mac.com"},
        "subject": subject,
        "textContent": body,
    }

    if attachment_path:
        p = Path(attachment_path)
        if p.exists() and p.is_file():
            mime, _ = mimetypes.guess_type(str(p))
            with p.open("rb") as fh:
                encoded = base64.b64encode(fh.read()).decode()
            payload["attachment"] = [
                {"name": p.name, "content": encoded}
            ]
        else:
            current_app.logger.warning("Attachment not found: %s", attachment_path)

    started = time.monotonic()
    current_app.logger.info(
        "📧 Sending email to: %s from %s via Brevo HTTP API", to_email, default_sender
    )
    try:
        resp = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=20,
        )
        elapsed = time.monotonic() - started
        if resp.status_code in (200, 201):
            current_app.logger.info("✅ Email sent via Brevo API in %.2fs", elapsed)
            return True, "OK"
        else:
            current_app.logger.error(
                "❌ Brevo API error %s: %s", resp.status_code, resp.text
            )
            return False, f"Brevo API error {resp.status_code}: {resp.text}"
    except requests.Timeout:
        current_app.logger.error("❌ Brevo API request timed out")
        return False, "Brevo API request timed out"
    except Exception as e:
        current_app.logger.error("❌ Brevo API call failed: %s", e, exc_info=True)
        return False, f"Brevo API call failed: {e}"


def _send_via_smtp(
    mail: Mail,
    to_email: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """Flask-Mail SMTP path (used when BREVO_API_KEY is not set)."""
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
        msg.reply_to = "donfox1@mac.com"
        msg.extra_headers = {"X-Mailer": "Flask-Mail", "X-Priority": "3"}

        if attachment_path:
            p = Path(attachment_path)
            if not p.exists() or not p.is_file():
                current_app.logger.warning("Attachment not found: %s", p)
            else:
                mime = _guess_mimetype(p)
                with p.open("rb") as fh:
                    msg.attach(filename=p.name, content_type=mime, data=fh.read())

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
