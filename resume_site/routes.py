# routes.py

import logging
import os
import secrets
from functools import wraps

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from sqlalchemy import text

from .models import EmailRequest, db
from .utils import validate_email

logger = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)


# Home page route
@main_bp.route("/")
def index():
    return render_template("index.html")


# Form to request a resume download
@main_bp.route("/resume", methods=["GET", "POST"])
def resume():
    if request.method == "POST":
        user_name = request.form.get("name")
        user_email = request.form.get("email")
        resume_format = request.form.get("format", "pdf")
        if resume_format not in ("pdf", "word"):
            resume_format = "pdf"
        ip_address = request.remote_addr

        user_name = user_name.strip() if user_name else ""
        if not user_name:
            flash("Please provide your name.", "danger")
            return redirect(url_for("main.resume"))
        if len(user_name) > 128:
            flash("Name must be 128 characters or fewer.", "danger")
            return redirect(url_for("main.resume"))

        if not user_email or not validate_email(user_email):
            flash("Please provide a valid email address.", "danger")
            return redirect(url_for("main.resume"))

        # --- Check/record request ---
        try:
            db.session.execute(text("SELECT 1"))
            existing_request = EmailRequest.query.filter_by(email=user_email).first()
            already_requested = existing_request is not None

            if not already_requested:
                db.session.add(
                    EmailRequest(
                        name=user_name, email=user_email, ip_address=ip_address
                    )
                )
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"DB error saving resume request: {e}")
            flash("An error occurred. Please try again.", "danger")
            return redirect(url_for("main.resume"))

        # --- Serve the file as a download ---
        filename = "Resume.v3.7.pdf" if resume_format == "pdf" else "Resume.v3.7.docx"
        files_dir = os.path.join(current_app.static_folder, "files")
        attachment_path = os.path.join(files_dir, filename)

        if not os.path.isfile(attachment_path):
            current_app.logger.error("Resume file not found: %s", attachment_path)
            flash("That resume file is unavailable right now. Please try again later.", "danger")
            return redirect(url_for("main.resume"))

        return send_from_directory(files_dir, filename, as_attachment=True)

    return render_template("resume.html")


@main_bp.route("/books")
def books():
    return render_template("books.html")


@main_bp.route("/references")
def references():
    return render_template("references.html")


def check_auth(password):
    # compare_digest avoids leaking password length/prefix via timing
    admin_password = os.getenv("ADMIN_PASSWORD")
    return bool(password) and bool(admin_password) and secrets.compare_digest(
        password, admin_password
    )


def authenticate():
    return Response(
        "Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@requires_auth
def email_requests():
    # Registered dynamically in create_app() at the path from ADMIN_ROUTE
    # (config.py), not via @main_bp.route — the URL is obscurity on top of
    # requires_auth, never a substitute for it.
    try:
        requests = EmailRequest.query.all()
        return render_template("email_requests.html", email_requests=requests)
    except Exception as e:
        current_app.logger.error(f"Failed to retrieve email requests: {e}")
        flash("An error occurred while retrieving data.", "danger")
        return redirect(url_for("main.index"))
