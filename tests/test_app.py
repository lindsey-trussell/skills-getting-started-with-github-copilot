"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create a test client
client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_dict(self):
        """Test that /activities endpoint returns a dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_fields(self):
        """Test that activities have required fields"""
        response = client.get("/activities")
        activities = response.json()

        # Check at least one activity exists
        assert len(activities) > 0

        # Check each activity has required fields
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_has_basketball(self):
        """Test that Basketball activity exists"""
        response = client.get("/activities")
        activities = response.json()
        assert "Basketball" in activities

    def test_get_activities_has_expected_count(self):
        """Test that we have multiple activities"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) >= 8  # At least 8 activities in the data


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Basketball/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "test@mergington.edu" in result["message"]

    def test_signup_duplicate_email_fails(self):
        """Test that signing up with duplicate email fails"""
        # First signup
        client.post("/activities/Basketball/signup?email=duplicate@mergington.edu")
        # Second signup with same email
        response = client.post(
            "/activities/Basketball/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]

    def test_signup_invalid_activity_fails(self):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/NonExistentActivity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]

    def test_participant_added_to_activity(self):
        """Test that participant is actually added to activity"""
        email = "verify@mergington.edu"
        client.post(f"/activities/Tennis Club/signup?email={email}")

        # Fetch activities and check
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Tennis Club"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        email = "unregister_test@mergington.edu"
        # First signup
        client.post(f"/activities/Drama Club/signup?email={email}")

        # Then unregister
        response = client.delete(
            f"/activities/Drama Club/unregister?email={email}"
        )
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]

    def test_unregister_removes_from_list(self):
        """Test that unregister actually removes participant from list"""
        email = "remove_test@mergington.edu"
        # Signup
        client.post(f"/activities/Art Studio/signup?email={email}")

        # Verify signup
        response = client.get("/activities")
        assert email in response.json()["Art Studio"]["participants"]

        # Unregister
        client.delete(f"/activities/Art Studio/unregister?email={email}")

        # Verify removal
        response = client.get("/activities")
        assert email not in response.json()["Art Studio"]["participants"]

    def test_unregister_non_existent_participant_fails(self):
        """Test that unregistering non-existent participant fails"""
        response = client.delete(
            "/activities/Debate Team/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not registered" in result["detail"]

    def test_unregister_invalid_activity_fails(self):
        """Test that unregister for non-existent activity fails"""
        response = client.delete(
            "/activities/FakeActivity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]


class TestIntegration:
    """Integration tests"""

    def test_full_signup_and_unregister_flow(self):
        """Test complete flow of signup and unregister"""
        email = "integration@mergington.edu"
        activity = "Science Club"

        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])

        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200

        # Verify signup increased count
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count + 1
        assert email in response.json()[activity]["participants"]

        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200

        # Verify unregister decreased count
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count
        assert email not in response.json()[activity]["participants"]

    def test_multiple_participants_per_activity(self):
        """Test multiple participants in same activity"""
        activity = "Chess Club"
        emails = ["multi1@mergington.edu", "multi2@mergington.edu", "multi3@mergington.edu"]

        # Sign up multiple participants
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

        # Verify all are registered
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
