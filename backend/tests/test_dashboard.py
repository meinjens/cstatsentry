import pytest
from fastapi.testclient import TestClient


class TestDashboardEndpoints:
    """Test dashboard endpoints"""

    def test_get_dashboard_summary_success(self, authenticated_client: TestClient):
        """Test successful dashboard summary retrieval"""
        response = authenticated_client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "total_matches",
            "total_players_analyzed",
            "suspicious_players",
            "high_risk_players",
            "new_detections_today",
            "last_sync"
        ]

        for field in required_fields:
            assert field in data

        assert isinstance(data["total_matches"], int)
        assert isinstance(data["total_players_analyzed"], int)
        assert isinstance(data["suspicious_players"], int)
        assert isinstance(data["high_risk_players"], int)
        assert isinstance(data["new_detections_today"], int)

    def test_get_dashboard_summary_unauthorized(self, client: TestClient):
        """Test dashboard summary without authentication"""
        response = client.get("/api/v1/dashboard/summary")
        assert response.status_code == 401

    def test_get_recent_activity_success(self, authenticated_client: TestClient):
        """Test successful recent activity retrieval"""
        response = authenticated_client.get("/api/v1/dashboard/recent")
        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "recent_analyses",
            "new_flags",
            "updated_players"
        ]

        for field in required_fields:
            assert field in data
            assert isinstance(data[field], list)

    def test_get_recent_activity_unauthorized(self, client: TestClient):
        """Test recent activity without authentication"""
        response = client.get("/api/v1/dashboard/recent")
        assert response.status_code == 401

    def test_get_user_statistics_success(self, authenticated_client: TestClient):
        """Test successful user statistics retrieval"""
        response = authenticated_client.get("/api/v1/dashboard/statistics")
        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "matches_by_month",
            "suspicion_score_distribution",
            "detection_trends",
            "most_common_flags"
        ]

        for field in required_fields:
            assert field in data

        assert isinstance(data["matches_by_month"], list)
        assert isinstance(data["suspicion_score_distribution"], dict)
        assert isinstance(data["detection_trends"], list)
        assert isinstance(data["most_common_flags"], list)

    def test_get_user_statistics_unauthorized(self, client: TestClient):
        """Test user statistics without authentication"""
        response = client.get("/api/v1/dashboard/statistics")
        assert response.status_code == 401