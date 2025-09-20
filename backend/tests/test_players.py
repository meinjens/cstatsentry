import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.crud.player import create_player


class TestPlayersEndpoints:
    """Test players endpoints"""

    @pytest.fixture
    def sample_player(self, db_session):
        """Create a test player"""
        player_data = {
            "steam_id": "76561198987654321",
            "current_name": "TestPlayer",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        return create_player(db_session, player_data)

    def test_get_player_success(self, authenticated_client: TestClient, db_session, sample_player, monkeypatch):
        """Test successful player retrieval"""
        def mock_get_player_by_steam_id(db, steam_id):
            return sample_player

        def mock_get_latest_player_analysis(db, steam_id):
            return None

        def mock_get_player_ban_info(db, steam_id):
            return None

        from app.crud import player
        monkeypatch.setattr(player, "get_player_by_steam_id", mock_get_player_by_steam_id)
        monkeypatch.setattr(player, "get_latest_player_analysis", mock_get_latest_player_analysis)
        monkeypatch.setattr(player, "get_player_ban_info", mock_get_player_ban_info)

        steam_id = sample_player.steam_id
        response = authenticated_client.get(f"/api/v1/players/{steam_id}")
        assert response.status_code == 200
        data = response.json()

        assert "steam_id" in data
        assert data["steam_id"] == steam_id

    def test_get_player_not_found(self, authenticated_client: TestClient, monkeypatch):
        """Test player not found"""
        def mock_get_player_by_steam_id(db, steam_id):
            return None

        from app.crud import player
        monkeypatch.setattr(player, "get_player_by_steam_id", mock_get_player_by_steam_id)

        steam_id = "76561198000000000"
        response = authenticated_client.get(f"/api/v1/players/{steam_id}")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Player not found"

    def test_get_player_unauthorized(self, client: TestClient):
        """Test player retrieval without authentication"""
        steam_id = "76561198987654321"
        response = client.get(f"/api/v1/players/{steam_id}")
        assert response.status_code == 401

    def test_get_player_analysis_history_success(self, authenticated_client: TestClient, db_session, sample_player, monkeypatch):
        """Test successful player analysis history retrieval"""
        def mock_get_player_by_steam_id(db, steam_id):
            return sample_player

        def mock_get_player_analyses(db, steam_id, limit):
            return []

        from app.crud import player
        monkeypatch.setattr(player, "get_player_by_steam_id", mock_get_player_by_steam_id)
        monkeypatch.setattr(player, "get_player_analyses", mock_get_player_analyses)

        steam_id = sample_player.steam_id
        response = authenticated_client.get(f"/api/v1/players/{steam_id}/analysis")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_player_analysis_history_with_limit(self, authenticated_client: TestClient, db_session, sample_player, monkeypatch):
        """Test player analysis history with custom limit"""
        def mock_get_player_by_steam_id(db, steam_id):
            return sample_player

        def mock_get_player_analyses(db, steam_id, limit):
            assert limit == 5
            return []

        from app.crud import player
        monkeypatch.setattr(player, "get_player_by_steam_id", mock_get_player_by_steam_id)
        monkeypatch.setattr(player, "get_player_analyses", mock_get_player_analyses)

        steam_id = sample_player.steam_id
        response = authenticated_client.get(f"/api/v1/players/{steam_id}/analysis?limit=5")
        assert response.status_code == 200

    def test_get_player_analysis_history_invalid_limit(self, authenticated_client: TestClient):
        """Test player analysis history with invalid limit"""
        steam_id = "76561198987654321"
        response = authenticated_client.get(f"/api/v1/players/{steam_id}/analysis?limit=200")
        assert response.status_code == 422

    def test_get_player_analysis_history_not_found(self, authenticated_client: TestClient, monkeypatch):
        """Test player analysis history for non-existent player"""
        def mock_get_player_by_steam_id(db, steam_id):
            return None

        from app.crud import player
        monkeypatch.setattr(player, "get_player_by_steam_id", mock_get_player_by_steam_id)

        steam_id = "76561198000000000"
        response = authenticated_client.get(f"/api/v1/players/{steam_id}/analysis")
        assert response.status_code == 404

    def test_get_player_analysis_history_unauthorized(self, client: TestClient):
        """Test player analysis history without authentication"""
        steam_id = "76561198987654321"
        response = client.get(f"/api/v1/players/{steam_id}/analysis")
        assert response.status_code == 401

    def test_trigger_player_analysis_success(self, authenticated_client: TestClient, db_session, sample_player, monkeypatch):
        """Test successful player analysis trigger"""
        def mock_get_player_by_steam_id(db, steam_id):
            return sample_player

        from app.crud import player
        monkeypatch.setattr(player, "get_player_by_steam_id", mock_get_player_by_steam_id)

        steam_id = sample_player.steam_id
        response = authenticated_client.post(f"/api/v1/players/{steam_id}/analyze")
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "status" in data
        assert steam_id in data["message"]
        assert data["status"] == "queued"

    def test_trigger_player_analysis_not_found(self, authenticated_client: TestClient, monkeypatch):
        """Test player analysis trigger for non-existent player"""
        def mock_get_player_by_steam_id(db, steam_id):
            return None

        from app.crud import player
        monkeypatch.setattr(player, "get_player_by_steam_id", mock_get_player_by_steam_id)

        steam_id = "76561198000000000"
        response = authenticated_client.post(f"/api/v1/players/{steam_id}/analyze")
        assert response.status_code == 404

    def test_trigger_player_analysis_unauthorized(self, client: TestClient):
        """Test player analysis trigger without authentication"""
        steam_id = "76561198987654321"
        response = client.post(f"/api/v1/players/{steam_id}/analyze")
        assert response.status_code == 401

    def test_get_suspicious_players_success(self, authenticated_client: TestClient):
        """Test successful suspicious players retrieval"""
        response = authenticated_client.get("/api/v1/players/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_suspicious_players_with_params(self, authenticated_client: TestClient):
        """Test suspicious players with custom parameters"""
        min_score = 80
        limit = 25
        response = authenticated_client.get(f"/api/v1/players/?min_suspicion_score={min_score}&limit={limit}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_suspicious_players_invalid_params(self, authenticated_client: TestClient):
        """Test suspicious players with invalid parameters"""
        # Test invalid suspicion score
        response = authenticated_client.get("/api/v1/players/?min_suspicion_score=150")
        assert response.status_code == 422

        # Test invalid limit
        response = authenticated_client.get("/api/v1/players/?limit=200")
        assert response.status_code == 422

    def test_get_suspicious_players_unauthorized(self, client: TestClient):
        """Test suspicious players without authentication"""
        response = client.get("/api/v1/players/")
        assert response.status_code == 401