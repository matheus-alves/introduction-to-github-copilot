from pathlib import Path
import sys
import copy

from fastapi.testclient import TestClient
import pytest

# Ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app as app_module

client = TestClient(app_module.app)

# Keep original activities to restore between tests
ORIGINAL = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def restore_activities():
    # Clear and restore a deep copy before each test to ensure isolation
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(ORIGINAL))
    yield


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    email = "testuser@example.com"
    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Signed up" in data["message"]
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_already_registered():
    # Use an existing participant to trigger the 400 error
    email = app_module.activities["Chess Club"]["participants"][0]
    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 400


def test_unregister_success():
    email = "toremove@example.com"
    # Add a participant then remove them
    app_module.activities["Programming Class"]["participants"].append(email)
    resp = client.post(f"/activities/Programming%20Class/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in app_module.activities["Programming Class"]["participants"]


def test_unregister_not_registered():
    email = "notfound@example.com"
    resp = client.post(f"/activities/Programming%20Class/unregister?email={email}")
    assert resp.status_code == 400
