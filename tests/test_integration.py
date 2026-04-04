def test_create_url_integration_db_check(client, app):
    """
    Integration Testing: Write tests that hit the API 
    (e.g., POST to /api/urls -> Check DB).
    """
    from app.models.url import URL
    
    # 1. Hit the API natively
    resp = client.post("/api/urls", json={
        "original_url": "https://integration.test.db"
    })
    
    assert resp.status_code == 201
    short_code = resp.json["short_code"]
    
    # 2. Query the database natively directly to ensure persistence
    with app.app_context():
        db_url = URL.get(URL.short_code == short_code)
        assert db_url.original_url == "https://integration.test.db"
