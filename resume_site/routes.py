# routes.py

import os
import logging
from flask import Response
from functools import wraps
from flask import current_app
from .extensions import mail

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
            current_app.logger.info("Mail extension loaded successfully")        

        success, message = send_email(
            mail,
            user_email,
            subject,
            body,
            attachment_path
        )

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
    return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.args.get("password") != os.getenv("ADMIN_PASSWORD"):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@main_bp.route("/secret-email-view-98347")
@requires_auth
def email_requests():
    try:
        requests = EmailRequest.query.all()
        return render_template("email_requests.html", email_requests=requests)
    except Exception as e:
        current_app.logger.error(f"Failed to retrieve email requests: {e}")
        flash("An error occurred while retrieving data.", "danger")
        return redirect(url_for("main.index"))


@main_bp.route("/test_email")
def test_email():
    from flask_mail import Message
    from .extensions import mail
    import traceback
    import sys
    import smtplib

    smtplib.SMTP.debuglevel = 1  # 🔍 Enable raw debug output

    msg = Message(
        subject="Test Email from Production",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=["donfox1@mac.com"],
        body="Production SMTP is working!"
    )

    try:
        mail.send(msg)
        return "✅ Test email sent successfully."
    except Exception as e:
        error_details = traceback.format_exc()
        current_app.logger.error("❌ Failed to send test email:")
        current_app.logger.error(error_details)
        return f"❌ Error sending email: {e}"


@main_bp.route("/test")
def test():
    return render_template("test.html")


@main_bp.route("/debug-photo")
def debug_photo():
    return '<img src="/static/images/don.jpg">'








