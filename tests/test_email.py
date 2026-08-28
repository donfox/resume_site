import os
import re
import tempfile


# --- Integration: POST /resume serves the file as a download ---
def test_resume_post_downloads_file(client, monkeypatch):
    # Patch on the module that USES this name (resume_site.routes), not resume_site.utils
    import resume_site.routes as routes_mod

    # Force validation to pass
    monkeypatch.setattr(routes_mod, "validate_email", lambda e: True, raising=True)

    payload = {"name": "Don R. Fox", "email": "donfox1@mac.com", "format": "pdf"}
    resp = client.post("/resume", data=payload, follow_redirects=False)

    assert resp.status_code == 200
    disposition = resp.headers.get("Content-Disposition", "")
    assert "attachment" in disposition
    assert re.search(r"resume\.v3\.7\.pdf", disposition, re.IGNORECASE)

    # Requesting the same email again should still trigger a download, not an error
    resp2 = client.post("/resume", data=payload, follow_redirects=False)
    assert resp2.status_code == 200
    assert "attachment" in resp2.headers.get("Content-Disposition", "")


# --- Invalid email path: should redirect back to /resume ---
def test_resume_post_invalid_email_redirects(client, monkeypatch):
    import resume_site.routes as routes_mod

    monkeypatch.setattr(routes_mod, "validate_email", lambda e: False, raising=True)

    resp = client.post(
        "/resume", data={"name": "X", "email": "not-an-email"}, follow_redirects=False
    )
    assert resp.status_code in (302, 303)
    assert "/resume" in resp.headers.get("Location", "")


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
