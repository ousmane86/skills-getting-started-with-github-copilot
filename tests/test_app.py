import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a copy of the original activities for resetting
ORIGINAL_ACTIVITIES = activities.copy()


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    global activities
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES)


def test_get_activities(client):
    """Test GET /activities endpoint"""
    # Arrange - nothing special needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # We have 9 activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    new_email = "test@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {new_email} for {activity_name}" in data["message"]
    # Verify the email was added to participants
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_activity_not_found(client):
    """Test signup for non-existent activity"""
    # Arrange
    invalid_activity = "NonExistent Club"
    email = "test@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_for_activity_already_signed_up(client):
    """Test signup when student is already signed up"""
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"  # Already in Chess Club

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" in data["detail"]


def test_remove_participant_success(client):
    """Test successful removal of a participant"""
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"  # Already in Chess Club

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participant",
        params={"email": email_to_remove}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Removed {email_to_remove} from {activity_name}" in data["message"]
    # Verify the email was removed from participants
    assert email_to_remove not in activities[activity_name]["participants"]


def test_remove_participant_activity_not_found(client):
    """Test removal from non-existent activity"""
    # Arrange
    invalid_activity = "NonExistent Club"
    email = "test@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{invalid_activity}/participant",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_remove_participant_not_found(client):
    """Test removal of participant not in activity"""
    # Arrange
    activity_name = "Chess Club"
    non_participant_email = "notparticipating@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participant",
        params={"email": non_participant_email}
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]