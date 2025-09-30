"""
Match sync using the new adapter pattern
This is the v2 implementation that uses provider adapters
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.celery import celery_app
from app.crud.match import create_match, get_match_by_id, create_match_player
from app.crud.player import get_player_by_steam_id, create_player, update_player
from app.crud.user import get_user_by_id
from app.db.session import SessionLocal
from app.models.user import User
from app.services.match_providers import get_match_provider, MatchData, MatchDetails

logger = logging.getLogger(__name__)


async def process_match_players_async_v2(
    db: Session,
    match_details: MatchDetails,
    match_id: str,
    user_id: int,
    user_steam_id: str
):
    """Process and create player records for a match using adapter data"""
    try:
        for player_perf in match_details.players:
            steam_id = player_perf.steam_id
            if not steam_id:
                continue

            # Check if player exists in our database
            existing_player = get_player_by_steam_id(db, steam_id)

            if not existing_player:
                # Create new player record
                player_record_data = {
                    "steam_id": steam_id,
                    "current_name": player_perf.player_name,
                    "profile_updated": None,
                    "stats_updated": None
                }
                create_player(db, player_record_data)
                logger.info(f"Created new player record for {steam_id}")
            else:
                # Update player name if different
                if player_perf.player_name and player_perf.player_name != existing_player.current_name:
                    update_player(db, existing_player, {"current_name": player_perf.player_name})

            # Create match player record
            headshot_percentage = 0
            if player_perf.kills > 0 and player_perf.headshots > 0:
                headshot_percentage = (player_perf.headshots / player_perf.kills) * 100

            match_player_data = {
                "match_id": match_id,
                "steam_id": steam_id,
                "team": player_perf.team,
                "kills": player_perf.kills,
                "deaths": player_perf.deaths,
                "assists": player_perf.assists,
                "headshot_percentage": headshot_percentage
            }

            create_match_player(db, match_player_data)
            logger.debug(f"Created match player record for {steam_id} in match {match_id}")

        # Extract and store teammate relationships
        # Find teammates (same team as user)
        user_team = None
        for player in match_details.players:
            if player.steam_id == user_steam_id:
                user_team = player.team
                break

        if user_team:
            teammate_steam_ids = [
                p.steam_id for p in match_details.players
                if p.team == user_team and p.steam_id != user_steam_id
            ]

            if teammate_steam_ids:
                logger.info(f"Found {len(teammate_steam_ids)} teammates for user {user_steam_id}")
                # Import here to avoid circular import
                from app.tasks.match_sync import store_teammate_relationships
                store_teammate_relationships(db, user_id, teammate_steam_ids)

    except Exception as e:
        logger.error(f"Error processing players for match {match_id}: {e}")
        raise


@celery_app.task(bind=True)
def fetch_user_matches_v2(self, user_id: int, limit: int = 10):
    """
    Fetch recent matches for a specific user using the adapter pattern
    This is the v2 implementation
    """
    db = SessionLocal()
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}

        if not user.sync_enabled:
            logger.info(f"Sync disabled for user {user_id}")
            return {"status": "skipped", "message": "Sync disabled"}

        logger.info(f"[v2] Fetching matches for user {user_id} (Steam ID: {user.steam_id})")

        matches_found = 0
        new_matches = 0

        async def fetch_matches_async():
            nonlocal matches_found, new_matches

            # Use the provider factory to get the configured provider
            async with get_match_provider() as provider:
                try:
                    logger.info(f"Using provider: {provider.provider_name}")

                    # If using Steam adapter, set user credentials
                    if provider.provider_name == "Steam":
                        if user.steam_auth_code and user.last_match_sharecode:
                            provider.set_user_credentials(
                                user.steam_auth_code,
                                user.last_match_sharecode
                            )
                        else:
                            logger.warning("[Steam] User has not configured Steam credentials")
                            logger.info("[Steam] User needs to set steam_auth_code and last_match_sharecode")
                            return

                    # Authenticate with the provider
                    if not await provider.authenticate(user.steam_id):
                        logger.error(f"[{provider.provider_name}] Authentication failed")
                        return

                    # Get recent matches
                    matches = await provider.get_recent_matches(user.steam_id, limit=limit)
                    matches_found = len(matches)
                    logger.info(f"[{provider.provider_name}] Found {matches_found} matches")

                    for match_data in matches:
                        match_id = match_data.match_id

                        if not match_id:
                            logger.warning(f"Skipping match with missing ID")
                            continue

                        # Check if match already exists
                        existing_match = get_match_by_id(db, match_id)
                        if existing_match:
                            logger.debug(f"Match {match_id} already exists, skipping")
                            continue

                        # Get detailed match information
                        match_details = await provider.get_match_details(match_id, user.steam_id)
                        if not match_details:
                            logger.warning(f"Could not get details for match {match_id}")
                            continue

                        # Create match record
                        try:
                            db_match_data = {
                                "match_id": match_id,
                                "user_id": user_id,
                                "match_date": match_data.started_at or datetime.utcnow(),
                                "map": match_data.map_name,
                                "score_team1": match_data.score_team1,
                                "score_team2": match_data.score_team2,
                                "leetify_match_id": match_id,  # Could be steam_match_id too
                                "sharing_code": match_data.sharecode,  # Store sharecode if available (Steam API)
                                "processed": False
                            }

                            created_match = create_match(db, db_match_data)
                            new_matches += 1
                            logger.info(f"Created match {match_id} for user {user_id}")

                            # Process players in this match
                            await process_match_players_async_v2(
                                db, match_details, match_id, user_id, user.steam_id
                            )

                        except Exception as e:
                            logger.error(f"Failed to create match {match_id}: {e}")
                            db.rollback()

                except Exception as e:
                    logger.error(f"[{provider.provider_name}] Failed to fetch matches: {e}")
                    db.rollback()

        # Run the async function
        asyncio.run(fetch_matches_async())

        # Update last_sync timestamp
        user.last_sync = datetime.utcnow()
        db.commit()

        return {
            "status": "completed",
            "user_id": user_id,
            "matches_found": matches_found,
            "new_matches": new_matches
        }

    except Exception as e:
        logger.error(f"Error fetching matches for user {user_id}: {e}")
        self.retry(countdown=60, max_retries=3)
    finally:
        db.close()