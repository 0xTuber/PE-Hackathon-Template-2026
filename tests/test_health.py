def test_health_check(client):
    """
    Pulse Check: Create a /health endpoint that returns 200 OK.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
