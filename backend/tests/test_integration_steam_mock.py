"""
Integration Tests with Mock Steam Service

These tests use the Docker-based mock Steam service to test
full authentication flows without hitting the real Steam API.
"""

import pytest
import httpx
import os
from fastapi.testclient import TestClient
from unittest.mock import patch


# Configuration for mock service
MOCK_STEAM_API_URL = os.getenv("MOCK_STEAM_API_URL", "http://localhost:5001")
MOCK_STEAM_OPENID_URL = f"{MOCK_STEAM_API_URL}/openid"


@pytest.fixture
def mock_steam_config(monkeypatch):
    """Configure app to use mock Steam service"""
    monkeypatch.setenv("STEAM_API_BASE_URL", MOCK_STEAM_API_URL)
    monkeypatch.setenv("STEAM_OPENID_URL", MOCK_STEAM_OPENID_URL)
    monkeypatch.setenv("STEAM_API_KEY", "test-steam-api-key")


@pytest.fixture
async def mock_steam_service_health():
    """Ensure mock Steam service is healthy before tests"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MOCK_STEAM_API_URL}/health", timeout=5.0)
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
    except Exception as e:
        pytest.skip(f"Mock Steam service not available: {e}")


@pytest.mark.integration
@pytest.mark.skip(reason="Complex integration setup necessary")
class TestSteamAuthIntegration:
    """Integration tests for Steam authentication with mock service"""

    def test_steam_login_url_generation(self, client: TestClient, mock_steam_config):
        """Test Steam login URL generation"""
        response = client.get("/api/v1/auth/steam/login")
        assert response.status_code == 200

        data = response.json()
        assert "auth_url" in data
        assert MOCK_STEAM_OPENID_URL in data["auth_url"]

    @pytest.mark.asyncio
    async def test_full_steam_auth_flow(self, client: TestClient, db_session, mock_steam_config, mock_steam_service_health):
        """Test complete Steam authentication flow with mock service"""

        # Step 1: Get login URL
        response = client.get("/api/v1/auth/steam/login")
        assert response.status_code == 200
        auth_url = response.json()["auth_url"]

        # Step 2: Simulate Steam callback with mock OpenID response
        callback_params = {
            "openid.mode": "id_res",
            "openid.claimed_id": "https://steamcommunity.com/openid/id/76561198123456789",
            "openid.identity": "https://steamcommunity.com/openid/id/76561198123456789",
            "openid.return_to": "http://localhost:3000/auth/steam/callback",
            "openid.response_nonce": "2023-01-01T00:00:00ZrKzYzQ",
            "openid.assoc_handle": "test_handle_123",
            "openid.signed": "signed,mode,identity,return_to,response_nonce,assoc_handle",
            "openid.sig": "test_signature_valid"
        }

        # Patch the Steam auth and API services to use mock
        with patch('app.services.steam_auth.steam_auth.verify_auth_response') as mock_verify, \
             patch('app.services.steam_api.steam_api.get_player_summaries') as mock_get_player:

            # Mock successful verification
            mock_verify.return_value = "76561198123456789"

            # Mock player data response
            mock_get_player.return_value = {
                "response": {
                    "players": [{
                        "steamid": "76561198123456789",
                        "personaname": "TestPlayer",
                        "avatar": "https://example.com/avatar_small.jpg",
                        "avatarmedium": "https://example.com/avatar_medium.jpg",
                        "avatarfull": "https://example.com/avatar_full.jpg",
                        "personastate": 1,
                        "communityvisibilitystate": 3,
                        "profilestate": 1
                    }]
                }
            }

            # Step 3: Process callback
            response = client.get("/api/v1/auth/steam/callback", params=callback_params, follow_redirects=False)
            assert response.status_code == 307  # Redirect response

            # Extract token and user data from redirect URL
            location = response.headers.get("location")
            assert location is not None
            assert "/auth/steam/callback" in location
            assert "token=" in location
            assert "user=" in location

            # Extract token from redirect URL for further testing
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(location)
            query_params = parse_qs(parsed_url.query)
            token = query_params["token"][0]

            # Step 4: Use token to access protected endpoint
            headers = {"Authorization": f"Bearer {token}"}

            response = client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code == 200

            user_data = response.json()
            assert user_data["steam_id"] == "76561198123456789"
            assert user_data["steam_name"] == "TestPlayer"

    @pytest.mark.asyncio
    async def test_steam_api_player_summaries_integration(self, mock_steam_config, mock_steam_service_health):
        """Test direct Steam API player summaries call with mock service"""
        async with httpx.AsyncClient() as client:
            # Test the mock Steam API directly
            response = await client.get(
                f"{MOCK_STEAM_API_URL}/ISteamUser/GetPlayerSummaries/v0002/",
                params={
                    "steamids": "76561198123456789",
                    "key": "test-steam-api-key"
                }
            )

            assert response.status_code == 200
            data = response.json()

            assert "response" in data
            assert "players" in data["response"]
            assert len(data["response"]["players"]) == 1

            player = data["response"]["players"][0]
            assert player["steamid"] == "76561198123456789"
            assert player["personaname"] == "TestPlayer"
            assert "avatar" in player

    @pytest.mark.asyncio
    async def test_steam_api_player_bans_integration(self, mock_steam_config, mock_steam_service_health):
        """Test Steam API player bans call with mock service"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MOCK_STEAM_API_URL}/ISteamUser/GetPlayerBans/v1/",
                params={
                    "steamids": "76561198123456789",
                    "key": "test-steam-api-key"
                }
            )

            assert response.status_code == 200
            data = response.json()

            assert "players" in data
            assert len(data["players"]) == 1

            ban_info = data["players"][0]
            assert ban_info["SteamId"] == "76561198123456789"
            assert ban_info["CommunityBanned"] is False
            assert ban_info["VACBanned"] is False
            assert ban_info["NumberOfVACBans"] == 0

    @pytest.mark.asyncio
    async def test_mock_steam_admin_endpoints(self, mock_steam_service_health):
        """Test mock Steam service admin endpoints"""
        async with httpx.AsyncClient() as client:
            # Test listing users
            response = await client.get(f"{MOCK_STEAM_API_URL}/admin/users")
            assert response.status_code == 200

            data = response.json()
            assert "users" in data
            assert "76561198123456789" in data["users"]

            # Test creating a new user
            new_user_data = {
                "steamid": "76561198999888777",
                "personaname": "NewTestUser",
                "avatar": "https://example.com/new_avatar.jpg"
            }

            response = await client.post(
                f"{MOCK_STEAM_API_URL}/admin/users",
                json=new_user_data
            )
            assert response.status_code == 200

            # Verify user was created
            response = await client.get(
                f"{MOCK_STEAM_API_URL}/ISteamUser/GetPlayerSummaries/v0002/",
                params={
                    "steamids": "76561198999888777",
                    "key": "test-key"
                }
            )
            assert response.status_code == 200

            data = response.json()
            assert len(data["response"]["players"]) == 1
            assert data["response"]["players"][0]["personaname"] == "NewTestUser"

            # Clean up - delete the test user
            response = await client.delete(f"{MOCK_STEAM_API_URL}/admin/users/76561198999888777")
            assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.skip(reason="Complex integration setup necessary")
class TestPlayerDataIntegration:
    """Integration tests for player data retrieval"""

    @pytest.mark.asyncio
    async def test_player_stats_retrieval(self, authenticated_client: TestClient, mock_steam_config, mock_steam_service_health):
        """Test retrieving player stats from mock Steam API"""

        # Mock the Steam API service to use our mock service
        with patch('app.services.steam_api.steam_api.get_user_stats_for_game') as mock_get_stats:
            mock_get_stats.return_value = {
                "playerstats": {
                    "steamID": "76561198123456789",
                    "gameName": "CS2",
                    "stats": [
                        {"name": "total_kills", "value": 1337},
                        {"name": "total_deaths", "value": 1000},
                        {"name": "total_time_played", "value": 123456}
                    ]
                }
            }

            # This endpoint would be implemented in your actual API
            # For now, we're testing the Steam API integration
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{MOCK_STEAM_API_URL}/ISteamUserStats/GetUserStatsForGame/v0002/",
                    params={
                        "steamid": "76561198123456789",
                        "appid": "730",  # CS2
                        "key": "test-key"
                    }
                )

                assert response.status_code == 200
                data = response.json()

                assert "playerstats" in data
                stats = data["playerstats"]["stats"]

                # Verify we got the expected stats
                stat_names = [stat["name"] for stat in stats]
                assert "total_kills" in stat_names
                assert "total_deaths" in stat_names
                assert "total_time_played" in stat_names


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndUserJourney:
    """End-to-end integration tests simulating full user journeys"""

    @pytest.mark.asyncio
    async def test_new_user_registration_and_analysis(self, client: TestClient, db_session, mock_steam_config, mock_steam_service_health):
        """Test complete user journey from registration to analysis"""

        # Step 1: User logs in via Steam
        callback_params = {
            "openid.mode": "id_res",
            "openid.claimed_id": "https://steamcommunity.com/openid/id/76561198999888777",
            "openid.identity": "https://steamcommunity.com/openid/id/76561198999888777",
            "openid.return_to": "http://localhost:3000/auth/steam/callback",
            "openid.response_nonce": "2023-01-01T00:00:00ZrKzYzQ",
            "openid.assoc_handle": "test_handle_123",
            "openid.signed": "signed,mode,identity,return_to,response_nonce,assoc_handle",
            "openid.sig": "test_signature_valid"
        }

        with patch('app.services.steam_auth.steam_auth.verify_auth_response') as mock_verify, \
             patch('app.services.steam_api.steam_api.get_player_summaries') as mock_get_player:

            mock_verify.return_value = "76561198999888777"
            mock_get_player.return_value = {
                "response": {
                    "players": [{
                        "steamid": "76561198999888777",
                        "personaname": "EndToEndTestUser",
                        "avatar": "https://example.com/e2e_avatar.jpg",
                        "avatarmedium": "https://example.com/e2e_avatar_medium.jpg",
                        "avatarfull": "https://example.com/e2e_avatar_full.jpg",
                    }]
                }
            }

            # User authenticates
            response = client.get("/api/v1/auth/steam/callback", params=callback_params, follow_redirects=False)
            assert response.status_code == 307  # Redirect response

            # Extract token from redirect URL
            location = response.headers.get("location")
            assert location is not None
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(location)
            query_params = parse_qs(parsed_url.query)
            token = query_params["token"][0]
            headers = {"Authorization": f"Bearer {token}"}

            # Step 2: User accesses dashboard
            response = client.get("/api/v1/dashboard/summary", headers=headers)
            assert response.status_code == 200

            # Step 3: User checks their profile
            response = client.get("/api/v1/users/me", headers=headers)
            assert response.status_code == 200

            user_data = response.json()
            assert user_data["steam_name"] == "EndToEndTestUser"

            # Step 4: User triggers match sync (placeholder)
            response = client.post("/api/v1/matches/sync", headers=headers)
            assert response.status_code == 200

            sync_data = response.json()
            assert "status" in sync_data