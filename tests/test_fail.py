"""
Intentional failure tests to verify the CI/CD pipeline
catches and reports test failures correctly.
"""

def test_intentional_failure_division():
    """This test deliberately fails to prove pipeline catches errors."""
    assert 1 / 1 == 2, "Intentional failure: verifying pipeline detects broken logic"

def test_intentional_failure_status_code(client):
    """Simulate an unexpected API response assertion."""
    resp = client.get("/health")
    assert resp.status_code == 500, "Intentional failure: expected 500 but health returns 200"
