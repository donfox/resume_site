# resume_site/__init__.py
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template
from dotenv import load_dotenv

from config import Config
from .extensions import db, mail, migrate
from .routes import main_bp


# Load .env next to project root (repo root = parent of resume_site/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


def create_app(config_object: dict | None = None) -> Flask:
    """Application factory for the resume site."""
    app = Flask(
        __name__,
        static_folder=Config.STATIC_FOLDER,
        instance_relative_config=True,
    )
    app.config.from_object(Config)
    if config_object:
        app.config.update(config_object)

    # --- Extensions ---
    db.init_app(app)

    # Ensure models are imported so Alembic sees metadata BEFORE migrate.init_app
    from . import models  # noqa: F401

    # Register Flask-Migrate CLI
    migrate.init_app(app, db)

    # Mail (tolerate missing creds in some envs)
    try:
        mail.init_app(app)
    except Exception:
        pass

    # --- Logging ---
    _configure_logging(app)

    # Safe summary (avoid printing full DATABASE_URL with creds)
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    backend = uri.split(":", 1)[0] if ":" in uri else uri
    mode = "debug" if app.debug else "production"
    app.logger.info("App initialized. DB backend=%s mode=%s", backend, mode)

    # --- Asset checks (optional) ---
    photo_path = Path(app.static_folder) / "images" / "don.jpg"
    if not photo_path.exists():
        app.logger.warning("Home photo not found at: %s", photo_path)
    for name in ("Resume.v3.7.pdf", "Resume.v3.7.docx"):
        resume_path = Path(app.static_folder) / "files" / name
        if not resume_path.exists():
            app.logger.warning("Missing resume file: %s", resume_path)

    # --- Blueprints ---
    app.register_blueprint(main_bp)

    # --- Context processor for templates ---
    @app.context_processor
    def inject_now():
        return {"now": datetime.now}

    # --- Error handlers ---
    @app.errorhandler(404)
    def handle_404_error(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def handle_500_error(e):
        return render_template("500.html"), 500

    # No db.create_all() here; we’ll use migrations.
    return app


def _configure_logging(app: Flask) -> None:
    """Attach console + rotating file handlers based on Config; avoid duplicates."""
    if app.logger.handlers:
        app.logger.handlers.clear()

    level = app.config.get("LOGGING_LEVEL", logging.INFO)
    fmt = app.config.get(
        "LOG_FORMAT", "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    )
    formatter = logging.Formatter(fmt)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    app.logger.addHandler(console)

    # File handler (skip in tests)
    if not app.testing:
        log_dir = Path(app.config.get("LOG_DIR", "logs"))
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file_cfg = app.config.get("LOG_FILE", "app.log")
        log_file = Path(log_file_cfg)
        if not log_file.is_absolute():
            log_file = log_dir / log_file.name

        max_bytes = int(app.config.get("MAX_LOG_SIZE", 100_000))
        backups = int(app.config.get("BACKUP_COUNT", 1))
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backups
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(level)
    app.logger.propagate = False

    # Quiet down Werkzeug unless you want per-request logs
    logging.getLogger("werkzeug").setLevel(level)
