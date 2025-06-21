# tests/test_utils.py

import os
import sys
import pytest
from unittest.mock import Mock, patch
from flask import Flask
from flask_mail import Mail
from resume_site.utils import send_email, validate_email, ensure_file_exists

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["MAIL_USERNAME"] = "test@example.com"
    app.config["TESTING"] = True
    app.config["MAIL_SUPPRESS_SEND"] = True
    return app


@pytest.fixture
def mail(app):
    return Mail(app)


def test_validate_email_valid():
    assert validate_email("user@example.com")


def test_validate_email_invalid():
    assert not validate_email("bad-email")


def test_validate_email_edge_cases():
    assert not validate_email("@example.com")
    assert not validate_email("user@.com")
    assert not validate_email("user@example")


def test_ensure_file_exists_logs_warning(tmp_path, caplog):
    test_path = tmp_path / "missing.txt"
    ensure_file_exists(str(test_path))
    assert "File not found" in caplog.text


def test_ensure_file_exists_no_warning(tmp_path, caplog):
    test_path = tmp_path / "exists.txt"
    test_path.write_text("content")
    ensure_file_exists(str(test_path))
    assert "File not found" not in caplog.text


def test_send_email_success(app, mail):
    with app.app_context():
        with patch.object(mail, "send") as mock_send:
            success, message = send_email(
                mail=mail,
                app=app,
                recipient="to@example.com",
                subject="Test Subject",
                body="Test Body",
            )
            assert success is True
            assert "has been sent" in message
            mock_send.assert_called_once()


def test_send_email_attachment_missing(app, mail):
    with app.app_context():
        success, message = send_email(
            mail=mail,
            app=app,
            recipient="to@example.com",
            subject="Test Subject",
            body="Test Body",
            attachment_path="nonexistent/path/resume.pdf",
        )
        assert success is True
        assert "has been sent" in message


def test_send_email_attachment_exists(app, mail, tmp_path):
    attachment_path = tmp_path / "resume.txt"
    attachment_path.write_text("This is the resume")
    with app.app_context():
        with patch.object(mail, "send") as mock_send:
            with patch("flask_mail.Message.attach") as mock_attach:
                send_email(
                    mail=mail,
                    app=app,
                    recipient="to@example.com",
                    subject="Test",
                    body="Body",
                    attachment_path=str(attachment_path),
                )
                mock_attach.assert_called_once()
                mock_send.assert_called_once()


def test_send_email_attachment_is_directory(app, tmp_path):
    dir_path = tmp_path / "resume_folder"
    dir_path.mkdir()
    with app.app_context():
        success, message = send_email(
            mail=Mail(app),
            app=app,
            recipient="to@example.com",
            subject="Test",
            body="Body",
            attachment_path=str(dir_path),
        )
        assert success is True


def test_send_email_failure(app):
    bad_mail = Mock()
    bad_mail.send.side_effect = Exception("SMTP failure")
    with app.app_context():
        success, message = send_email(
            mail=bad_mail,
            app=app,
            recipient="fail@example.com",
            subject="Oops",
            body="Failure test",
        )
        assert success is False
        assert "Error sending email" in message
