import pytest
from fastapi.testclient import TestClient


class TestUsersEndpoints:
    """Test users endpoints"""

    def test_get_current_user_profile_success(self, authenticated_client: TestClient):
        """Test successful current user profile retrieval"""
        response = authenticated_client.get("/api/v1/users/me")
        assert response.status_code == 200
        data = response.json()

        required_fields = ["steam_id", "steam_name"]
        for field in required_fields:
            assert field in data

        assert data["steam_id"] == "76561198123456789"

    def test_get_current_user_profile_unauthorized(self, client: TestClient):
        """Test current user profile without authentication"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_update_current_user_profile_success(self, authenticated_client: TestClient, monkeypatch):
        """Test successful user profile update"""
        def mock_update_user(db, user, update_data):
            user.steam_name = update_data.get("steam_name", user.steam_name)
            user.sync_enabled = update_data.get("sync_enabled", user.sync_enabled)
            return user

        from app.crud import user
        monkeypatch.setattr(user, "update_user", mock_update_user)

        update_data = {
            "steam_name": "UpdatedName",
            "sync_enabled": False
        }

        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        assert response.status_code == 200
        data = response.json()

        assert "steam_id" in data
        assert data["steam_id"] == "76561198123456789"

    def test_update_current_user_profile_partial_update(self, authenticated_client: TestClient, monkeypatch):
        """Test partial user profile update"""
        def mock_update_user(db, user, update_data):
            for key, value in update_data.items():
                setattr(user, key, value)
            return user

        from app.crud import user
        monkeypatch.setattr(user, "update_user", mock_update_user)

        update_data = {
            "sync_enabled": True
        }

        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        assert response.status_code == 200
        data = response.json()

        assert "steam_id" in data

    def test_update_current_user_profile_empty_body(self, authenticated_client: TestClient, monkeypatch):
        """Test user profile update with empty body"""
        def mock_update_user(db, user, update_data):
            return user

        from app.crud import user
        monkeypatch.setattr(user, "update_user", mock_update_user)

        response = authenticated_client.put("/api/v1/users/me", json={})
        assert response.status_code == 200

    def test_update_current_user_profile_invalid_data(self, authenticated_client: TestClient):
        """Test user profile update with invalid data types"""
        update_data = {
            "steam_name": 12345,  # should be string
            "sync_enabled": "not_a_boolean"  # should be boolean
        }

        response = authenticated_client.put("/api/v1/users/me", json=update_data)
        assert response.status_code == 422

    def test_update_current_user_profile_unauthorized(self, client: TestClient):
        """Test user profile update without authentication"""
        update_data = {
            "steam_name": "NewName"
        }

        response = client.put("/api/v1/users/me", json=update_data)
        assert response.status_code == 401

    def test_update_current_user_profile_malformed_json(self, authenticated_client: TestClient):
        """Test user profile update with malformed JSON"""
        response = authenticated_client.put(
            "/api/v1/users/me",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422