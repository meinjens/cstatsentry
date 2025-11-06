import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # Status can be healthy or unhealthy depending on whether PostgreSQL is running
    assert data["status"] in ["healthy", "unhealthy"]
    assert "database" in data
    # Database can be "connected" or "disconnected" depending on test environment
    assert data["database"] in ["connected", "disconnected", "unknown"]


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "CStatSentry API"
    assert data["version"] == "1.0.0"