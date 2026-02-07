# routes.py

import os
import logging
from functools import wraps
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
    Response,
)
from sqlalchemy import text

from .models import db, EmailRequest
from .utils import send_email, validate_email

logger = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)


def get_admin_route():
    """Get admin route from config, with fallback."""
    return current_app.config.get("ADMIN_ROUTE", "/admin-email-requests")


# Home page route
@main_bp.route("/")
def index():
    return render_template("index.html")


# Form to request resume delivery by email
@main_bp.route("/resume", methods=["GET", "POST"])
def resume():
    if request.method == "POST":
        user_name = request.form.get("name")
        user_email = request.form.get("email")
        resume_format = request.form.get("format", "pdf")
        ip_address = request.remote_addr

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

        # --- Send email ---
        subject = f"Resume for Don Fox - {resume_format.upper()}"
        body = (
            f"Hello{' ' + user_name if user_name else ''},\n\n"
            "Thank you for your interest in my professional background. "
            f"I've attached my resume in {resume_format.upper()} format as requested.\n\n"
            "The resume includes details about my experience in:\n"
            "- Backend Systems Development (C/C++, Python, Perl, Elixir)\n"
            "- Healthcare IT and Medical Systems\n"
            "- Unix/Linux Platform Engineering\n"
            "- Database Design and Optimization\n\n"
            "Feel free to reach out if you have any questions or would like to discuss "
            "potential opportunities.\n\n"
            "Best regards,\n"
            "Don Fox\n"
            "donfox1@mac.com\n"
            "(865) 360-0089"
        )
        filename = "Resume.v3.7.pdf" if resume_format == "pdf" else "Resume.v3.7.docx"
        attachment_path = os.path.join(current_app.static_folder, "files", filename)

        mail = current_app.extensions.get("mail")
        if not mail:
            current_app.logger.error("Mail extension not initialized!")
            flash(
                "Email service is unavailable right now. Please try again later.",
                "danger",
            )
            return redirect(url_for("main.resume"))

        success, message = send_email(mail, user_email, subject, body, attachment_path)

        # --- Flash exactly one message ---
        if success:
            if already_requested:
                flash(
                    "You've already requested a resume. Sending another copy!", "info"
                )
            else:
                flash(f"Your résumé was sent to {user_email}.", "success")
        else:
            flash(f"Could not send email: {message}", "danger")

        return redirect(url_for("main.resume"))

    return render_template("resume.html")


@main_bp.route("/books")
def books():
    return render_template("books.html")


@main_bp.route("/references")
def references():
    return render_template("references.html")


def check_auth(password):
    return password == os.getenv("ADMIN_PASSWORD")


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


@main_bp.route("/admin-email-requests")
@requires_auth
def email_requests():
    # Note: Route path can be customized via ADMIN_ROUTE environment variable
    # but this provides a sensible default. For production, set a unique path.
    try:
        requests = EmailRequest.query.all()
        return render_template("email_requests.html", email_requests=requests)
    except Exception as e:
        current_app.logger.error(f"Failed to retrieve email requests: {e}")
        flash("An error occurred while retrieving data.", "danger")
        return redirect(url_for("main.index"))
