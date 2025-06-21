# config.py

import os
import logging

basedir = os.path.abspath(os.getcwd())
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

load_dotenv(override=True)


def str_to_bool(value):
    return value.lower() in ("true", "1", "t", "y", "yes")


class Config:
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = ENV == "development"

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(basedir, 'instance', 'site.db')}"
    )
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = str_to_bool(os.getenv("MAIL_USE_TLS", "True"))
    MAIL_USE_SSL = str_to_bool(os.getenv("MAIL_USE_SSL", "False"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", None)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    # Log settings
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_FOLDER = os.path.join(BASE_DIR, "static")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    LOG_FILE = os.path.join(LOG_DIR, "app.log")
    MAX_LOG_SIZE = 100000  # 100 KB
    BACKUP_COUNT = 1

    if not SECRET_KEY or not ADMIN_PASSWORD:
        raise ValueError(
            "SECRET_KEY and ADMIN_PASSWORD must be set in the environment."
        )

    @staticmethod
    def setup_logging():
        if not os.path.exists(Config.LOG_DIR):
            os.makedirs(Config.LOG_DIR)

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                RotatingFileHandler(
                    Config.LOG_FILE,
                    maxBytes=Config.MAX_LOG_SIZE,
                    backupCount=Config.BACKUP_COUNT,
                ),
                logging.StreamHandler(),
            ],
        )

        logger.info("Logging is successfully configured.")


# Call setup_logging() at the start of application.
Config.setup_logging()
