def test_list_urls_empty(client):
    resp = client.get("/api/urls")
    assert resp.status_code == 200
    assert resp.json == []

def test_create_url(client):
    resp = client.post("/api/urls", json={
        "original_url": "https://example.com",
        "title": "Example"
    })
    assert resp.status_code == 201
    assert "short_code" in resp.json
    assert resp.json["original_url"] == "https://example.com"
    assert "created_at" in resp.json
    assert "updated_at" in resp.json

def test_create_url_missing_fields(client):
    resp = client.post("/api/urls", json={
        "title": "Example"
    })
    assert resp.status_code == 400
    assert "error" in resp.json

def test_redirect_valid_shortcode(client):
    """Ensure accessing a shortcode triggers a 302 redirect."""
    create_resp = client.post("/api/urls", json={
        "original_url": "https://example.com"
    })
    short_code = create_resp.json["short_code"]
    
    # Testing the redirect endpoint
    redirect_resp = client.get(f"/{short_code}")
    assert redirect_resp.status_code == 302
    assert redirect_resp.headers["Location"] == "https://example.com"

def test_redirect_invalid_shortcode(client):
    """Invalid code should 404."""
    resp = client.get("/invalid123")
    assert resp.status_code == 404
    assert "error" in resp.json