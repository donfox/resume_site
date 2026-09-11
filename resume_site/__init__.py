# resume_site/__init__.py
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template

from config import Config

from .extensions import db, migrate
from .routes import email_requests, main_bp

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

    # Registered directly on the app (not via @main_bp.route) so the path can
    # come from ADMIN_ROUTE, only known once app.config is loaded above.
    # main_bp is a module-level singleton reused across create_app() calls
    # (e.g. once per test), and Flask forbids add_url_rule on a blueprint
    # that's already been registered to any app — hence registering on app.
    app.add_url_rule(
        app.config["ADMIN_ROUTE"],
        endpoint="main.email_requests",
        view_func=email_requests,
    )

    # --- Context processor for templates ---
    @app.context_processor
    def inject_now():
        return {"now": datetime.now}

    # --- Error handlers ---
    @app.errorhandler(403)
    def handle_403_error(e):
        app.logger.warning(f"403 Forbidden: {e}")
        return render_template("403.html"), 403

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
