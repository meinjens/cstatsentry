import pytest
from fastapi.testclient import TestClient


class TestMatchesEndpoints:
    """Test matches endpoints"""

    def test_get_user_matches_success(self, authenticated_client: TestClient):
        """Test successful match history retrieval"""
        response = authenticated_client.get("/api/v1/matches/")
        assert response.status_code == 200
        data = response.json()

        required_fields = ["matches", "total", "limit", "offset"]
        for field in required_fields:
            assert field in data

        assert isinstance(data["matches"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["offset"], int)
        assert data["limit"] == 50  # default limit
        assert data["offset"] == 0   # default offset

    def test_get_user_matches_with_params(self, authenticated_client: TestClient):
        """Test match history with custom parameters"""
        limit = 25
        offset = 10
        response = authenticated_client.get(f"/api/v1/matches/?limit={limit}&offset={offset}")
        assert response.status_code == 200
        data = response.json()

        assert data["limit"] == limit
        assert data["offset"] == offset

    def test_get_user_matches_invalid_params(self, authenticated_client: TestClient):
        """Test match history with invalid parameters"""
        # Test limit too high
        response = authenticated_client.get("/api/v1/matches/?limit=200")
        assert response.status_code == 422

        # Test negative offset
        response = authenticated_client.get("/api/v1/matches/?offset=-1")
        assert response.status_code == 422

        # Test limit too low
        response = authenticated_client.get("/api/v1/matches/?limit=0")
        assert response.status_code == 422

    def test_get_user_matches_unauthorized(self, client: TestClient):
        """Test match history without authentication"""
        response = client.get("/api/v1/matches/")
        assert response.status_code == 401

    def test_get_match_details_not_found(self, authenticated_client: TestClient):
        """Test getting details for non-existent match"""
        match_id = "nonexistent_match_id"
        response = authenticated_client.get(f"/api/v1/matches/{match_id}")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Match not found"

    def test_get_match_details_unauthorized(self, client: TestClient):
        """Test match details without authentication"""
        match_id = "some_match_id"
        response = client.get(f"/api/v1/matches/{match_id}")
        assert response.status_code == 401

    def test_trigger_match_sync_success(self, authenticated_client: TestClient):
        """Test successful match synchronization trigger"""
        response = authenticated_client.post("/api/v1/matches/sync")
        assert response.status_code == 200
        data = response.json()

        required_fields = ["message", "user_id", "status"]
        for field in required_fields:
            assert field in data

        assert data["message"] == "Match synchronization started"
        assert data["status"] == "queued"
        assert data["user_id"] is not None

    def test_trigger_match_sync_unauthorized(self, client: TestClient):
        """Test match sync trigger without authentication"""
        response = client.post("/api/v1/matches/sync")
        assert response.status_code == 401

    def test_get_sync_status_success(self, authenticated_client: TestClient):
        """Test successful sync status retrieval"""
        response = authenticated_client.get("/api/v1/matches/sync/status")
        assert response.status_code == 200
        data = response.json()

        required_fields = ["status", "last_sync", "sync_enabled"]
        for field in required_fields:
            assert field in data

        assert data["status"] in ["idle", "running", "completed", "failed"]
        assert isinstance(data["sync_enabled"], bool)

    def test_get_sync_status_unauthorized(self, client: TestClient):
        """Test sync status without authentication"""
        response = client.get("/api/v1/matches/sync/status")
        assert response.status_code == 401