def test_list_users_empty(client):
    """Ensure it starts out empty."""
    resp = client.get("/api/users")
    assert resp.status_code == 200
    assert resp.json == []

def test_create_user(client):
    """Test standard user creation."""
    resp = client.post("/api/users", json={
        "username": "testuser",
        "email": "test@example.com"
    })
    assert resp.status_code == 201
    assert resp.json["username"] == "testuser"
    assert resp.json["email"] == "test@example.com"
    assert "created_at" in resp.json

def test_create_user_duplicate(client):
    """Ensure duplicate usernames/emails conflict."""
    client.post("/api/users", json={
        "username": "testuser",
        "email": "test@example.com"
    })
    
    resp = client.post("/api/users", json={
        "username": "testuser",
        "email": "test@example.com"
    })
    assert resp.status_code == 409
    assert "error" in resp.json

def test_get_user(client):
    """Test retrieving existing user by ID."""
    resp_create = client.post("/api/users", json={
        "username": "john",
        "email": "john@example.com"
    })
    uid = resp_create.json["id"]
    
    resp_get = client.get(f"/api/users/{uid}")
    assert resp_get.status_code == 200
    assert resp_get.json["username"] == "john"

def test_get_user_not_found(client):
    """Test invalid user IDs."""
    resp = client.get("/api/users/999")
    assert resp.status_code == 404
    assert "error" in resp.json

def test_create_user_missing_fields(client):
    """Test missing JSON body parameters."""
    resp = client.post("/api/users", json={
        "username": "testuser"
    })
    assert resp.status_code == 400
    assert "error" in resp.json