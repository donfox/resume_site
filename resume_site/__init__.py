import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from config import Config

from .routes import main_bp
from .extensions import db, mail

from dotenv import load_dotenv
import smtplib
smtplib.SMTP.debuglevel = 0  # Disable smtplib verbose output

load_dotenv()

# Create and configure the Flask app
def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    static_dir = os.path.join(base_dir, "static")

    app = Flask(__name__, static_folder=Config.STATIC_FOLDER)
    app.config.from_object(Config)

    # Logging setup
    if not os.path.exists(app.config["LOG_DIR"]):
        os.makedirs(app.config["LOG_DIR"])


    # Logging setup: file + console (Render-friendly)
    file_handler = RotatingFileHandler(
        app.config["LOG_FILE"],
        maxBytes=app.config["MAX_LOG_SIZE"],
        backupCount=app.config["BACKUP_COUNT"],
    )
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    file_handler.setLevel(app.config.get("LOG_LEVEL", logging.INFO))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    stream_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

    app.logger.info("Logging is successfully configured.")
    app.logger.info(" Flask app initialized")

    # Asset checks
    photo_path = os.path.join(app.static_folder, "images", "don.jpg")
    if not os.path.exists(photo_path):
        app.logger.warning(f"⚠️  Home photo not found at: {photo_path}")

    resume_files = ["Resume.v3.4.pdf", "Resume.v3.4.docx"]
    resume_dir = os.path.join(app.static_folder, "files")
    for resume in resume_files:
        resume_path = os.path.join(resume_dir, resume)
        if not os.path.exists(resume_path):
            app.logger.warning(f"⚠️  Missing resume file: {resume_path}")

    db.init_app(app)
    mail.init_app(app)
    app.register_blueprint(main_bp)

    from .utils import validate_config
    validate_config(app)

    if app.config["ENV"] == "development":
        with app.app_context():
            db.create_all()

    return app