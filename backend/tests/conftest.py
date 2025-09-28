import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token
from app.crud.player import create_player
from app.crud.user import create_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_player(db_session):
    """Create a test player for stats testing"""
    player_data = {
        "steam_id": "76561198123456789",
        "current_name": "TestPlayer",
        "avatar_url": "https://example.com/avatar.jpg",
        "profile_url": "https://steamcommunity.com/profiles/76561198123456789",
        "cs2_hours": 500,
        "total_games_owned": 50
    }
    player = create_player(db_session, player_data)
    return player


@pytest.fixture
def test_user(db_session, test_player):
    user_data = {
        "steam_id": "76561198123456789",
        "steam_name": "TestUser",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    user = create_user(db_session, user_data)
    return user


@pytest.fixture
def test_user_token(test_user):
    return create_access_token(subject=test_user.steam_id)


@pytest.fixture
def authenticated_client(client, test_user_token):
    client.headers = {
        **getattr(client, 'headers', {}),
        "Authorization": f"Bearer {test_user_token}"
    }
    return client


@pytest.fixture
def sample_steam_auth_response():
    return {
        "openid.mode": "id_res",
        "openid.claimed_id": "https://steamcommunity.com/openid/id/76561198123456789",
        "openid.identity": "https://steamcommunity.com/openid/id/76561198123456789",
        "openid.return_to": "http://localhost:3000/auth/steam/callback",
        "openid.response_nonce": "2023-01-01T00:00:00ZrKzYzQ",
        "openid.assoc_handle": "1234567890",
        "openid.signed": "signed,mode,identity,return_to,response_nonce,assoc_handle",
        "openid.sig": "test_signature"
    }


@pytest.fixture
def sample_steam_player_data():
    return {
        "response": {
            "players": [{
                "steamid": "76561198123456789",
                "personaname": "TestPlayer",
                "avatar": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/test_small.jpg",
                "avatarmedium": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/test_medium.jpg",
                "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/test_full.jpg",
                "personastate": 1,
                "communityvisibilitystate": 3,
                "profilestate": 1,
                "realname": "Test Player",
                "primaryclanid": "103582791429521408",
                "timecreated": 1234567890,
                "personastateflags": 0
            }]
        }
    }


@pytest.fixture
def mock_steam_auth_success(monkeypatch, sample_steam_player_data):
    async def mock_verify_auth_response(params):
        return "76561198123456789"

    async def mock_get_player_summaries(steam_ids):
        return sample_steam_player_data

    from app.services.steam_auth import steam_auth

    # Mock the factory function to return a client with mocked methods
    def mock_get_steam_api_client():
        from app.services.steam_api import SteamAPIClient

        class MockSteamAPIClient(SteamAPIClient):
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client = MockSteamAPIClient()
        client.get_player_summaries = mock_get_player_summaries
        return client

    monkeypatch.setattr(steam_auth, "verify_auth_response", mock_verify_auth_response)
    monkeypatch.setattr("app.api.api_v1.endpoints.auth.get_steam_api_client", mock_get_steam_api_client)


@pytest.fixture
def mock_steam_auth_failure(monkeypatch):
    async def mock_verify_auth_response(params):
        return None

    from app.services.steam_auth import steam_auth
    monkeypatch.setattr(steam_auth, "verify_auth_response", mock_verify_auth_response)


@pytest.fixture
def test_admin_user(db_session):
    """Create an admin user for testing"""
    user_data = {
        "steam_id": "76561198999999999",
        "steam_name": "AdminUser",
        "avatar_url": "https://example.com/admin_avatar.jpg",
        "is_admin": True
    }
    user = create_user(db_session, user_data)
    return user


@pytest.fixture
def test_admin_token(test_admin_user):
    """Create an admin token for testing"""
    return create_access_token(subject=test_admin_user.steam_id)


@pytest.fixture
def admin_client(client, test_admin_token):
    """Client with admin authentication"""
    client.headers = {
        **getattr(client, 'headers', {}),
        "Authorization": f"Bearer {test_admin_token}"
    }
    return client


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_player_data():
    """Sample player data for testing"""
    return {
        "steam_id": "76561198123456789",
        "current_name": "TestPlayer",
        "profile_url": "https://steamcommunity.com/id/testplayer",
        "avatar_url": "https://example.com/avatar.jpg",
        "country": "US",
        "state": "CA",
        "city": "San Francisco"
    }


@pytest.fixture
def sample_match_data():
    """Sample match data for testing"""
    return {
        "match_id": "CSGO-Test-Match-123",
        "demo_url": "https://example.com/demo.dem",
        "map_name": "de_dust2",
        "game_mode": "competitive",
        "started_at": "2023-01-01T12:00:00Z",
        "finished_at": "2023-01-01T13:00:00Z",
        "score_team1": 16,
        "score_team2": 14
    }