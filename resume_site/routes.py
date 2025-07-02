# routes.py

import os
import logging

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
)
from sqlalchemy import text

from .models import db, EmailRequest, UserMessage
from .utils import send_email, validate_email

logger = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)


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

        current_app.logger.info(
            f"Received resume request from {user_name} ({user_email}) at {ip_address}"
        )

        if not user_email or not validate_email(user_email):
            flash("Please provide a valid email address.", "danger")
            current_app.logger.warning(f"Invalid email address provided: {user_email}")
            return redirect(url_for("main.resume"))

        try:
            print(">>> DB check starting")
            db.session.execute(text("SELECT 1"))
            existing_request = EmailRequest.query.filter_by(email=user_email).first()

            if existing_request:
                flash(
                    "You've already requested a resume. Sending another copy!", "info"
                )
            else:
                new_request = EmailRequest(
                    name=user_name, email=user_email, ip_address=ip_address
                )
                db.session.add(new_request)
                db.session.commit()
                current_app.logger.info(f"New resume request recorded: {user_name}, {user_email}")

        except Exception as e:
            print(">>> DB exception occurred:", e)
            db.session.rollback()
            current_app.logger.error(f"Database error while saving resume request: {e}")
            flash("An error occurred. Please try again.", "danger")
            return redirect(url_for("main.resume"))

        subject = "Your Requested Resume"
        body = (
            f"Hello {user_name},\n\nThank you for your interest. "
            "Attached is the resume you requested."
        )

        filename = "Resume.v3.4.pdf" if resume_format == "pdf" else "Resume.v3.4.docx"
        attachment_path = os.path.join(current_app.static_folder, "files", filename)

        mail = current_app.extensions.get("mail")

        if not mail:
            current_app.logger.error("Mail extension not initialized!")
        else:
            current_app.logger.warning("Mail extension loaded successfully")        

        current_app.logger.warning("About to call send_email")

        success, message = send_email(
            mail, current_app, user_email, subject, body, attachment_path
        )
        flash(message, "success" if success else "danger")
        return redirect(url_for("main.resume"))

    return render_template("resume.html")


@main_bp.route("/books")
def books():
    return render_template("books.html")


@main_bp.route("/references")
def references():
    return render_template("references.html")


@main_bp.route("/secret-email-view-98347")
def email_requests():
    try:
        requests = EmailRequest.query.all()
        return render_template("email_requests.html", email_requests=requests)
    except Exception as e:
        current_app.logger.error(f"Failed to retrieve email requests: {e}")
        flash("An error occurred while retrieving data.", "danger")
        return redirect(url_for("main.index"))


@main_bp.route("/test")
def test():
    return render_template("test.html")


@main_bp.route("/debug-photo")
def debug_photo():
    return '<img src="/static/images/don.jpg">'
