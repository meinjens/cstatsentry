"""
Leetify-specific match sync task
Handles fetching matches from Leetify API
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.core.celery import celery_app
from app.crud.match import create_match, get_match_by_id, create_match_player
from app.crud.player import get_player_by_steam_id, create_player, update_player
from app.db.session import SessionLocal
from app.services.leetify_api import get_leetify_api_client, LeetifyDataExtractor

logger = logging.getLogger(__name__)


async def process_match_players_async(db: Session, match_details: dict, match_id: str, user_steam_id: str, user_id: int):
    """Process and create player records for a match from Leetify data"""
    try:
        players = match_details.get("players", [])

        for player_data in players:
            steam_id = player_data.get("steamId")
            if not steam_id:
                continue

            # Extract player performance data
            performance_data = LeetifyDataExtractor.extract_player_performance(player_data, match_id)

            # Check if player exists in our database
            existing_player = get_player_by_steam_id(db, steam_id)

            if not existing_player:
                # Create new player record
                player_record_data = {
                    "steam_id": steam_id,
                    "current_name": player_data.get("name", "Unknown"),
                    "profile_updated": None,
                    "stats_updated": None
                }
                create_player(db, player_record_data)
                logger.info(f"[Leetify] Created new player record for {steam_id}")
            else:
                # Update player name if different
                if player_data.get("name") and player_data["name"] != existing_player.current_name:
                    update_player(db, existing_player, {"current_name": player_data["name"]})

            # Create match player record
            match_player_data = {
                "match_id": match_id,
                "steam_id": steam_id,
                "team": performance_data.get("team", 1),
                "kills": performance_data.get("kills", 0),
                "deaths": performance_data.get("deaths", 0),
                "assists": performance_data.get("assists", 0),
                "headshot_percentage": performance_data.get("headshots", 0) / max(performance_data.get("kills", 1), 1) * 100 if performance_data.get("headshots") else 0
            }

            create_match_player(db, match_player_data)
            logger.debug(f"[Leetify] Created match player record for {steam_id} in match {match_id}")

        # Extract and store teammate relationships
        from app.tasks.match_sync import store_teammate_relationships
        teammates = LeetifyDataExtractor.extract_teammates(match_details, user_steam_id)
        if teammates:
            logger.info(f"[Leetify] Found {len(teammates)} teammates for user {user_steam_id} in match {match_id}")
            store_teammate_relationships(db, user_id, teammates)

    except Exception as e:
        logger.error(f"[Leetify] Error processing players for match {match_id}: {e}")
        raise


@celery_app.task(bind=True, name="tasks.sync_leetify_matches")
def sync_leetify_matches(self, user_id: int, steam_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    Fetch matches from Leetify API for a specific user

    Args:
        user_id: Database user ID
        steam_id: Steam ID of the user
        limit: Maximum number of matches to fetch

    Returns:
        Dictionary with sync results
    """
    db = SessionLocal()
    try:
        logger.info(f"[Leetify] Starting match sync for Steam ID {steam_id}")

        matches_found = 0
        new_matches = 0

        async def fetch_matches_async():
            nonlocal matches_found, new_matches
            async with get_leetify_api_client() as leetify_api:
                try:
                    # Get recent games from Leetify API
                    games = await leetify_api.get_recent_games(steam_id, limit=limit)
                    matches_found = len(games)
                    logger.info(f"[Leetify] Found {matches_found} matches for Steam ID {steam_id}")

                    for game in games:
                        # Extract match data
                        match_data = LeetifyDataExtractor.extract_match_data(game)
                        match_id = match_data["match_id"]

                        if not match_id:
                            logger.warning(f"[Leetify] Skipping match with missing ID for user {steam_id}")
                            continue

                        # Check if match already exists
                        existing_match = get_match_by_id(db, match_id)
                        if existing_match:
                            logger.debug(f"[Leetify] Match {match_id} already exists, skipping")
                            continue

                        # Get detailed match information
                        match_details = await leetify_api.get_game_details(match_id, steam_id)
                        if not match_details:
                            logger.warning(f"[Leetify] Could not get details for match {match_id}")
                            continue

                        # Create match record
                        try:
                            db_match_data = {
                                "match_id": match_id,
                                "user_id": user_id,
                                "match_date": match_data.get("started_at") or datetime.utcnow(),
                                "map": match_data.get("map_name"),
                                "score_team1": match_data.get("score_team1"),
                                "score_team2": match_data.get("score_team2"),
                                "leetify_match_id": match_id,
                                "processed": False
                            }

                            create_match(db, db_match_data)
                            new_matches += 1
                            logger.info(f"[Leetify] Created match {match_id} for Steam ID {steam_id}")

                            # Process players in this match
                            await process_match_players_async(db, match_details, match_id, steam_id, user_id)

                        except Exception as e:
                            logger.error(f"[Leetify] Failed to create match {match_id} for Steam ID {steam_id}: {e}")
                            db.rollback()

                except Exception as e:
                    logger.error(f"[Leetify] Failed to fetch matches from API for Steam ID {steam_id}: {e}")
                    db.rollback()
                    raise

        # Run the async function
        asyncio.run(fetch_matches_async())

        return {
            "status": "completed",
            "source": "leetify",
            "user_id": user_id,
            "matches_found": matches_found,
            "new_matches": new_matches
        }

    except Exception as e:
        logger.error(f"[Leetify] Error syncing matches for Steam ID {steam_id}: {e}")
        self.retry(countdown=60, max_retries=3)
    finally:
        db.close()
