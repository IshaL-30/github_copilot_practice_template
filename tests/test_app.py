import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = copy.deepcopy(original)


def test_root_redirects_to_index():
    # Arrange

    # Act
    response = client.get("/", allow_redirects=False)

    # Assert
    assert response.status_code in (301, 302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    # Arrange

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    path = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    original_count = len(app_module.activities[activity]["participants"])

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert len(app_module.activities[activity]["participants"]) == original_count + 1
    assert email in app_module.activities[activity]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    path = f"/activities/{quote(activity)}/signup?email={quote(email)}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_unsubscribes_student():
    # Arrange
    activity = "Chess Club"
    email = "daniel@mergington.edu"
    assert email in app_module.activities[activity]["participants"]
    path = f"/activities/{quote(activity)}/participants?email={quote(email)}"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity}"
    assert email not in app_module.activities[activity]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity = "Chess Club"
    email = "unknown@mergington.edu"
    path = f"/activities/{quote(activity)}/participants?email={quote(email)}"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
