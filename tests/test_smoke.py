def test_homepage_ok(client):
    """Basic availability check."""
    resp = client.get("/")
    assert resp.status_code == 200
    # Optional: ensure some identifying text appears
    assert b"Resume" in resp.data or b"Programming" in resp.data or b"Home" in resp.data


def test_404_for_unknown_page(client):
    resp = client.get("/this-page-should-not-exist")
    assert resp.status_code in (404, 308, 301)  # some apps redirect to 404 page