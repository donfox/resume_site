# tests/conftest.py
import os
import sys
import tempfile

import pytest

# Ensure repo root on path
SYS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SYS_ROOT not in sys.path:
    sys.path.insert(0, SYS_ROOT)

from resume_site import create_app  # noqa: E402
from resume_site.extensions import db  # noqa: E402


@pytest.fixture
def app():
    """Flask app on a throwaway SQLite file, so tests never touch the dev DB."""
    fd, db_path = tempfile.mkstemp(prefix="test_", suffix=".db")
    os.close(fd)
    flask_app = create_app(
        {
            "TESTING": True,
            "DEBUG": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        }
    )
    with flask_app.app_context():
        db.create_all()
    yield flask_app
    with flask_app.app_context():
        db.session.remove()
        db.engine.dispose()
    os.remove(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
