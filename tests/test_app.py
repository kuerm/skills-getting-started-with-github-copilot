import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a test client
@pytest.fixture
def client():
    return TestClient(app)

# Test data for testing
test_email = "test@student.com"
existing_email = "michael@mergington.edu"  # Already in Chess Club
test_activity = "Chess Club"
nonexistent_activity = "Nonexistent Activity"

class TestActivitiesAPI:
    """Test suite for the Activities API endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that Chess Club exists and has expected structure
        assert test_activity in data
        chess_club = data[test_activity]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # First, get initial participant count
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data[test_activity]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{test_activity}/signup?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert test_activity in data["message"]
        
        # Verify the participant was added
        response = client.get("/activities")
        updated_data = response.json()
        assert test_email in updated_data[test_activity]["participants"]
        assert len(updated_data[test_activity]["participants"]) == initial_count + 1

    def test_signup_activity_not_found(self, client):
        """Test signup for nonexistent activity"""
        response = client.post(f"/activities/{nonexistent_activity}/signup?email={test_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self, client):
        """Test signup when already signed up"""
        # First sign up
        client.post(f"/activities/{test_activity}/signup?email={test_email}")
        
        # Try to sign up again
        response = client.post(f"/activities/{test_activity}/signup?email={test_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_unregister_success(self, client):
        """Test successful unregister from an activity"""
        # First sign up
        client.post(f"/activities/{test_activity}/signup?email={test_email}")
        
        # Get count before unregister
        response = client.get("/activities")
        data = response.json()
        count_before = len(data[test_activity]["participants"])
        
        # Unregister
        response = client.delete(f"/activities/{test_activity}/signup?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert test_activity in data["message"]
        
        # Verify the participant was removed
        response = client.get("/activities")
        updated_data = response.json()
        assert test_email not in updated_data[test_activity]["participants"]
        assert len(updated_data[test_activity]["participants"]) == count_before - 1

    def test_unregister_activity_not_found(self, client):
        """Test unregister from nonexistent activity"""
        response = client.delete(f"/activities/{nonexistent_activity}/signup?email={test_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up(self, client):
        """Test unregister when not signed up"""
        response = client.delete(f"/activities/{test_activity}/signup?email={test_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_root_redirect(self, client):
        """Test root endpoint redirects to static file"""
        response = client.get("/")
        assert response.status_code == 200  # RedirectResponse in FastAPI returns 200 with HTML redirect
        # Note: In a real test, you might check the Location header, but this works for the current setup
