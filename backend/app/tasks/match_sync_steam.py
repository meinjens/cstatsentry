"""
Steam-specific match sync task
Handles fetching matches from Steam API using sharecode iteration
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.core.celery import celery_app
from app.crud.match import create_match, get_match_by_id
from app.crud.user import get_user_by_id
from app.db.session import SessionLocal
from app.services.steam_match_history import SteamMatchHistoryService
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.sync_steam_matches")
def sync_steam_matches(self, user_id: int, steam_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    Fetch matches from Steam API for a specific user using sharecode iteration

    Args:
        user_id: Database user ID
        steam_id: Steam ID of the user
        limit: Maximum number of matches to fetch

    Returns:
        Dictionary with sync results
    """
    db = SessionLocal()
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            logger.error(f"[Steam] User {user_id} not found")
            return {"status": "error", "source": "steam", "message": "User not found"}

        # Check if user has provided Steam auth credentials
        if not user.steam_auth_code or not user.last_match_sharecode:
            logger.info(f"[Steam] User {user_id} has not provided Steam auth credentials, skipping")
            return {
                "status": "skipped",
                "source": "steam",
                "message": "Steam auth code and sharecode not configured",
                "matches_found": 0,
                "new_matches": 0
            }

        logger.info(f"[Steam] Starting match sync for user {user_id} (Steam ID: {steam_id})")

        matches_found = 0
        new_matches = 0

        async def fetch_matches_async():
            nonlocal matches_found, new_matches

            try:
                async with SteamMatchHistoryService(settings.STEAM_API_KEY) as steam_service:
                    # Fetch match history using sharecode iteration
                    raw_matches = await steam_service.fetch_match_history(
                        steam_id,
                        user.steam_auth_code,
                        user.last_match_sharecode,
                        limit=limit
                    )

                    matches_found = len(raw_matches)
                    logger.info(f"[Steam] Found {matches_found} matches for user {user_id}")

                    for raw_match in raw_matches:
                        match_id = str(raw_match["match_id"])

                        # Check if match already exists
                        existing_match = get_match_by_id(db, match_id)
                        if existing_match:
                            logger.debug(f"[Steam] Match {match_id} already exists, skipping")
                            continue

                        # Create match record with sharecode
                        # Note: Detailed stats will be fetched later via demo parsing
                        try:
                            db_match_data = {
                                "match_id": match_id,
                                "user_id": user_id,
                                "match_date": datetime.utcnow(),  # Actual date from demo parsing later
                                "map": None,  # Will be populated from demo parsing
                                "score_team1": None,
                                "score_team2": None,
                                "sharing_code": raw_match["sharecode"],
                                "processed": False
                            }

                            create_match(db, db_match_data)
                            new_matches += 1
                            logger.info(f"[Steam] Created match {match_id} for user {user_id} with sharecode")

                            # Update user's last known sharecode to the most recent one
                            if new_matches == 1:  # First match is the most recent
                                user.last_match_sharecode = raw_match["sharecode"]
                                db.commit()
                                logger.debug(f"[Steam] Updated last_match_sharecode for user {user_id}")

                        except Exception as e:
                            logger.error(f"[Steam] Failed to create match {match_id}: {e}")
                            db.rollback()

            except Exception as e:
                logger.error(f"[Steam] Failed to fetch matches from API: {e}")
                db.rollback()
                raise

        # Run the async function
        asyncio.run(fetch_matches_async())

        return {
            "status": "completed",
            "source": "steam",
            "user_id": user_id,
            "matches_found": matches_found,
            "new_matches": new_matches
        }

    except Exception as e:
        logger.error(f"[Steam] Error syncing matches for user {user_id}: {e}")
        self.retry(countdown=60, max_retries=3)
    finally:
        db.close()
