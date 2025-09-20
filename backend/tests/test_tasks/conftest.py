import pytest
from unittest.mock import MagicMock, patch
from celery import Celery
from app.core.celery import celery_app
from app.models.user import User
from app.models.player import Player, PlayerBan
from app.crud.user import create_user
from app.crud.player import create_player


@pytest.fixture
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        'task_always_eager': True,
        'task_eager_propagates': True,
    }


@pytest.fixture
def celery_worker_parameters():
    return {
        'perform_ping_check': False,
    }


@pytest.fixture
def mock_steam_api():
    with patch('app.services.steam_api.steam_api') as mock:
        # Configure mock for async context manager
        mock.__aenter__ = MagicMock(return_value=mock)
        mock.__aexit__ = MagicMock(return_value=None)

        # Mock API methods
        mock.get_player_summaries.return_value = {
            "response": {
                "players": [{
                    "steamid": "76561198123456789",
                    "personaname": "TestPlayer",
                    "avatar": "https://example.com/avatar.jpg",
                    "avatarmedium": "https://example.com/avatar_medium.jpg",
                    "avatarfull": "https://example.com/avatar_full.jpg",
                    "personastate": 1,
                    "communityvisibilitystate": 3,
                    "profilestate": 1,
                    "timecreated": 1234567890,
                    "realname": "Test Player"
                }]
            }
        }

        mock.get_player_bans.return_value = {
            "players": [{
                "SteamId": "76561198123456789",
                "CommunityBanned": False,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 0,
                "NumberOfGameBans": 0,
                "EconomyBan": "none"
            }]
        }

        mock.get_owned_games.return_value = {
            "response": {
                "game_count": 10,
                "games": [
                    {"appid": 730, "playtime_forever": 500},  # CS2
                    {"appid": 440, "playtime_forever": 200}   # TF2
                ]
            }
        }

        yield mock


@pytest.fixture
def test_user_for_tasks(db_session):
    user_data = {
        "steam_id": "76561198123456789",
        "steam_name": "TestUser",
        "avatar_url": "https://example.com/avatar.jpg",
        "sync_enabled": True
    }
    return create_user(db_session, user_data)


@pytest.fixture
def test_player_for_tasks(db_session):
    from datetime import datetime
    player_data = {
        "steam_id": "76561198987654321",
        "current_name": "TestPlayer",
        "avatar_url": "https://example.com/avatar.jpg",
        "visibility_state": 3,
        "total_games_owned": 10,
        "cs2_hours": 500,
        "account_created": datetime.utcnow(),
        "profile_updated": datetime.utcnow()
    }
    return create_player(db_session, player_data)


@pytest.fixture
def mock_session_local():
    with patch('app.tasks.match_sync.SessionLocal') as mock_sl_match, \
         patch('app.tasks.player_analysis.SessionLocal') as mock_sl_analysis, \
         patch('app.tasks.steam_data_update.SessionLocal') as mock_sl_update:
        yield {
            'match_sync': mock_sl_match,
            'player_analysis': mock_sl_analysis,
            'steam_data_update': mock_sl_update
        }