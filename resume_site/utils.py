# resume_site/utils.py
from __future__ import annotations

import re

# --- Email validation ---

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> bool:
    """Basic email format check using regex."""
    return bool(email and EMAIL_REGEX.match(email))
