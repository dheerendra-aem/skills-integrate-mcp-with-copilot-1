from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)


def test_signup_and_unregister_flow():
    # pick a known seeded activity
    activities = client.get("/activities").json()
    name = list(activities.keys())[0]
    email = "teststudent@example.com"

    resp = client.post(f"/activities/{name}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # unregister
    resp = client.delete(f"/activities/{name}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")
