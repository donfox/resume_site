# tests/conftest.py
import os
import sys
import tempfile
import pytest

# Ensure repo root on path
SYS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SYS_ROOT not in sys.path:
    sys.path.insert(0, SYS_ROOT)

# Initialize these BEFORE we reference them
_create_app = None
_flask_app_instance = None

# Prefer your package name 'resume_site'
try:
    from resume_site import create_app as _create_app  # type: ignore
except Exception:
    try:
        from resume_site import app as _flask_app_instance  # type: ignore
    except Exception:
        pass

# Fallback to 'app' package name if needed
if _create_app is None and _flask_app_instance is None:
    try:
        from app import create_app as _create_app  # type: ignore
    except Exception:
        try:
            from app import app as _flask_app_instance  # type: ignore
        except Exception:
            pass


@pytest.fixture(scope="session")
def test_db_path():
    fd, path = tempfile.mkstemp(prefix="test_", suffix=".db")
    os.close(fd)
    yield path
    try:
        os.remove(path)
    except OSError:
        pass


@pytest.fixture
def app(test_db_path, monkeypatch):
    """
    Provides a Flask app configured for testing.
    """
    config_overrides = {
        "TESTING": True,
        "DEBUG": False,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "MAIL_SUPPRESS_SEND": True,
        "MAIL_SERVER": "localhost",
        "MAIL_PORT": 8025,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": False,
        "MAIL_DEFAULT_SENDER": os.getenv("MAIL_DEFAULT_SENDER", "test@example.com"),
        "LOG_LEVEL": "DEBUG",
    }

    # Build the Flask app
    if _create_app is not None:
        try:
            flask_app = _create_app(testing=True, config_overrides=config_overrides)  # your create_app has no kwargs
        except TypeError:
            flask_app = _create_app()
            flask_app.config.update(config_overrides)
    elif _flask_app_instance is not None:
        flask_app = _flask_app_instance
        flask_app.config.update(config_overrides)
    else:
        raise ImportError(
            "Could not locate your Flask app. Tried 'resume_site' and 'app' packages."
        )

    # Optional: create tables if SQLAlchemy present
    with flask_app.app_context():
        db = None
        try:
            from resume_site.extensions import db as _db  # type: ignore
            db = _db
        except Exception:
            try:
                from app.extensions import db as _db  # type: ignore
                db = _db
            except Exception:
                pass
        if db is not None:
            try:
                db.create_all()
            except Exception:
                pass

    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()