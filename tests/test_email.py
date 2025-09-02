import os
import re
import pytest
import tempfile

# --- Integration: POST /resume triggers send_email once (patch where it's used) ---
def test_resume_post_sends_email_success(client, monkeypatch):
    # Patch on the module that USES these names (resume_site.routes), not resume_site.utils
    import resume_site.routes as routes_mod

    # Force validation to pass
    monkeypatch.setattr(routes_mod, "validate_email", lambda e: True, raising=True)

    called = {}
    def fake_send_email(mail, to, subject, body, attachment_path):
        called["args"] = (mail, to, subject, body, attachment_path)
        return True, "OK"

    # Important: patch the symbol in routes_mod, because routes.py did `from .utils import send_email`
    monkeypatch.setattr(routes_mod, "send_email", fake_send_email, raising=True)

    payload = {"name": "Don R. Fox", "email": "donfox1@mac.com", "format": "pdf"}
    resp = client.post("/resume", data=payload, follow_redirects=True)
    assert resp.status_code in (200, 302)

    # Ensure our fake was called
    assert "args" in called
    _mail, to, subject, body, attachment_path = called["args"]
    assert to == "donfox1@mac.com"
    assert re.search(r"resume", subject, re.IGNORECASE)
    assert os.path.basename(attachment_path).lower() in ("resume.v3.4.pdf", "resume.v3.4.docx")


# --- Invalid email path: should redirect back to /resume ---
def test_resume_post_invalid_email_redirects(client, monkeypatch):
    import resume_site.routes as routes_mod
    monkeypatch.setattr(routes_mod, "validate_email", lambda e: False, raising=True)

    resp = client.post("/resume", data={"name": "X", "email": "not-an-email"}, follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert "/resume" in resp.headers.get("Location", "")


# --- /test_email route: ensure Mail.send is called exactly once ---

def test_test_email_route_uses_mail_send(client, monkeypatch):
    try:
        from flask_mail import Mail as _MailClass
    except Exception:
        pytest.skip("Flask-Mail not installed")

    app = client.application
    with app.app_context():
        app.config["MAIL_SUPPRESS_SEND"] = True  # safety

    sent = {"count": 0}
    def fake_send(self, message):  # class-level patch => needs (self, message)
        sent["count"] += 1

    # Patch the class so ANY Mail instance uses our fake
    monkeypatch.setattr(_MailClass, "send", fake_send, raising=True)

    resp = client.get("/test_email")
    assert resp.status_code == 200
    assert sent["count"] == 1
    

# --- Unit: utils.send_email attaches a PDF and calls Mail.send ---

def test_email_with_pdf_attachment(app, monkeypatch):
    from resume_site import utils
    import tempfile, os

    mail = app.extensions.get("mail")
    assert mail is not None

    captured = {}
    def fake_send(message):  # instance-level patch ⇒ no `self`
        captured["message"] = message

    # Patch the *instance* so we intercept the real object the app uses
    monkeypatch.setattr(mail, "send", fake_send, raising=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(b"%PDF-1.4\n% minimal test pdf\n")
        tmp_path = tmp.name

    try:
        with app.app_context():
            app.config["MAIL_SUPPRESS_SEND"] = True
            ok, msg = utils.send_email(
                mail,
                "donfox1@mac.com",
                "Resume PDF",
                "Attached is your resume.",
                tmp_path,
            )
            assert ok is True
    finally:
        os.remove(tmp_path)

    assert "message" in captured
    m = captured["message"]
    assert "Resume PDF" in m.subject
    assert "donfox1@mac.com" in m.recipients
    filenames = [att.filename for att in getattr(m, "attachments", [])]
    assert any(name and name.endswith(".pdf") for name in filenames)