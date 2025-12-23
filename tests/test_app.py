import copy
from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def restore_activities():
    """Backup the in-memory activities dict before each test and restore after."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser1@example.com"

    # Ensure not present initially
    assert email not in app_module.activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Duplicate signup should return 400
    resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_dup.status_code == 400

    # Unregister
    resp_unreg = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp_unreg.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # Unregistering again should return 400
    resp_unreg_again = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp_unreg_again.status_code == 400


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup?email=noone@example.com")
    assert resp.status_code == 404


def test_unregister_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/unregister?email=noone@example.com")
    assert resp.status_code == 404
