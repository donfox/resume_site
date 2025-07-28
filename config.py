import os
import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(level=logging.DEBUG)
from dotenv import load_dotenv
from pathlib import Path

# Load from .env if present (safe in both dev and production)
load_dotenv(override=True)

# basedir = os.path.abspath(os.getcwd())
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'instance', 'site.db')}"

def str_to_bool(value):
    return value.lower() in ("true", "1", "t", "y", "yes")

# Determine environment
ENV = os.getenv("FLASK_ENV", "production")

# Load and validate DATABASE_URL with fallback to SQLite in dev
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if not DATABASE_URL:
    if ENV == "development":
        DATABASE_URL = "sqlite:///dev.db"
    else:
        raise RuntimeError("❌ DATABASE_URL is not set in the environment.")

print("✅ DATABASE_URL resolved to:", DATABASE_URL)

# Load and validate critical secrets
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if not SECRET_KEY or not ADMIN_PASSWORD:
    raise ValueError("SECRET_KEY and ADMIN_PASSWORD must be set in the environment.")

class Config:
    DEBUG = ENV == "development"
    SECRET_KEY = SECRET_KEY
    ADMIN_PASSWORD = ADMIN_PASSWORD

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_DEBUG = 0
    MAIL_SERVER = os.getenv("BREVO_MAIL_SERVER") or os.getenv("MAIL_SERVER")
    MAIL_USERNAME = os.getenv("BREVO_MAIL_USERNAME") or os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("BREVO_MAIL_PASSWORD") or os.getenv("MAIL_PASSWORD")
    MAIL_PORT = int(os.getenv("BREVO_MAIL_PORT") or os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = str_to_bool(os.getenv("BREVO_MAIL_USE_TLS") or os.getenv("MAIL_USE_TLS", "True"))
    MAIL_USE_SSL = str_to_bool(os.getenv("MAIL_USE_SSL", "False"))
    # MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    MAIL_DEFAULT_SENDER = os.getenv("BREVO_MAIL_DEFAULT_SENDER") or os.getenv("MAIL_DEFAULT_SENDER")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    STATIC_FOLDER = os.path.join(basedir, "static")

    LOGGING_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    LOG_DIR = os.path.join(basedir, "logs")
    LOG_FILE = os.path.join(LOG_DIR, "app.log")
    MAX_LOG_SIZE = 100000  # 100 KB
    BACKUP_COUNT = 1