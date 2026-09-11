import re


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
