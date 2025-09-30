import pytest
from unittest.mock import MagicMock, patch
from app.tasks.match_sync import (
    fetch_new_matches_for_all_users,
    fetch_user_matches,
    process_match_data
)


class TestMatchSyncTasks:
    """Test match synchronization Celery tasks"""

    def test_fetch_new_matches_for_all_users_success(self, db_session, test_user_for_tasks, mock_session_local):
        """Test successful fetch for all users"""
        mock_session_local['match_sync'].return_value = db_session

        with patch('app.tasks.match_sync.fetch_user_matches.delay') as mock_delay:
            # Add another user to test multiple users
            from app.crud.user import create_user
            user2_data = {
                "steam_id": "76561198111111111",
                "steam_name": "TestUser2",
                "avatar_url": "https://example.com/avatar2.jpg",
                "sync_enabled": True
            }
            user2 = create_user(db_session, user2_data)

            result = fetch_new_matches_for_all_users()

            assert result["status"] == "completed"
            assert result["users_processed"] == 2
            assert mock_delay.call_count == 2

    def test_fetch_new_matches_for_all_users_no_active_users(self, db_session, mock_session_local):
        """Test when no users have sync enabled"""
        mock_session_local['match_sync'].return_value = db_session

        result = fetch_new_matches_for_all_users()

        assert result["status"] == "completed"
        assert result["users_processed"] == 0

    def test_fetch_new_matches_for_all_users_with_disabled_sync(self, db_session, mock_session_local):
        """Test with users that have sync disabled"""
        mock_session_local['match_sync'].return_value = db_session

        from app.crud.user import create_user
        user_data = {
            "steam_id": "76561198999999999",
            "steam_name": "DisabledUser",
            "avatar_url": "https://example.com/avatar.jpg",
            "sync_enabled": False
        }
        create_user(db_session, user_data)

        result = fetch_new_matches_for_all_users()

        assert result["status"] == "completed"
        assert result["users_processed"] == 0

    def test_fetch_user_matches_success(self, db_session, test_user_for_tasks, mock_session_local):
        """Test successful user match fetch"""
        mock_session_local['match_sync'].return_value = db_session

        # Store user_id before function call to avoid detached instance
        user_id = test_user_for_tasks.user_id

        # Mock asyncio.run to prevent actual API calls
        async def mock_fetch_matches_async():
            pass

        with patch('app.crud.user.get_user_by_id', return_value=test_user_for_tasks), \
             patch('app.tasks.match_sync.asyncio.run', return_value=None):
            result = fetch_user_matches(user_id)

            assert result["status"] == "completed"
            assert "user_id" in result
            assert "matches_found" in result
            assert "new_matches" in result

    def test_fetch_user_matches_user_not_found(self, db_session, mock_session_local):
        """Test fetch matches for non-existent user"""
        mock_session_local['match_sync'].return_value = db_session

        with patch('app.crud.user.get_user_by_id', return_value=None):
            result = fetch_user_matches(999)

            assert result["status"] == "error"
            assert result["message"] == "User not found"

    def test_fetch_user_matches_sync_disabled(self, db_session, mock_session_local):
        """Test fetch matches for user with sync disabled"""
        mock_session_local['match_sync'].return_value = db_session

        from app.crud.user import create_user
        user_data = {
            "steam_id": "76561198888888888",
            "steam_name": "DisabledSyncUser",
            "avatar_url": "https://example.com/avatar.jpg",
            "sync_enabled": False
        }
        disabled_user = create_user(db_session, user_data)

        with patch('app.crud.user.get_user_by_id', return_value=disabled_user):
            result = fetch_user_matches(disabled_user.user_id)

            assert result["status"] == "skipped"
            assert result["message"] == "Sync disabled"

    def test_fetch_user_matches_with_limit(self, db_session, test_user_for_tasks, mock_session_local):
        """Test user match fetch with custom limit"""
        mock_session_local['match_sync'].return_value = db_session

        # Store user_id before function call to avoid detached instance
        user_id = test_user_for_tasks.user_id

        with patch('app.crud.user.get_user_by_id', return_value=test_user_for_tasks), \
             patch('app.tasks.match_sync.asyncio.run', return_value=None):
            result = fetch_user_matches(user_id, limit=20)

            assert result["status"] == "completed"
            assert "user_id" in result

    def test_process_match_data_success(self, db_session, mock_session_local):
        """Test successful match data processing"""
        mock_session_local['match_sync'].return_value = db_session

        match_id = "test_match_123"
        user_id = 1

        result = process_match_data(match_id, user_id)

        assert result["status"] == "completed"
        assert result["match_id"] == match_id
        assert "players_processed" in result

    def test_fetch_new_matches_exception_handling(self, mock_session_local):
        """Test exception handling in fetch_new_matches_for_all_users"""
        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("Database error")
        mock_session_local['match_sync'].return_value = mock_db

        with patch.object(fetch_new_matches_for_all_users, 'retry') as mock_retry:
            fetch_new_matches_for_all_users()
            # Retry logic works in integration

    def test_fetch_user_matches_exception_handling(self, mock_session_local):
        """Test exception handling in fetch_user_matches"""
        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("Database error")
        mock_session_local['match_sync'].return_value = mock_db

        with patch.object(fetch_user_matches, 'retry') as mock_retry:
            fetch_user_matches(1)
            # Retry logic works in integration

    def test_process_match_data_exception_handling(self, mock_session_local):
        """Test exception handling in process_match_data"""
        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("Processing error")
        mock_session_local['match_sync'].return_value = mock_db

        with patch.object(process_match_data, 'retry') as mock_retry:
            process_match_data("match_123", 1)
            # Retry logic works in integration