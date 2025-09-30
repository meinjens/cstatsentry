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
from app.services.leetify_api import get_leetify_api_client, LeetifyDataExtractor

logger = logging.getLogger(__name__)


async def process_match_players_async(db: Session, match_details: dict, match_id: str, user_steam_id: str):
    """Process and create player records for a match"""
    try:
        # Extract players from match details
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
                # Create new player record - we'll fetch full Steam data later
                player_record_data = {
                    "steam_id": steam_id,
                    "current_name": player_data.get("name", "Unknown"),
                    "profile_updated": None,  # Will be updated when we fetch full Steam data
                    "stats_updated": None
                }
                create_player(db, player_record_data)
                logger.info(f"Created new player record for {steam_id}")
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
            logger.debug(f"Created match player record for {steam_id} in match {match_id}")

        # Extract and store teammate relationships for the user
        teammates = LeetifyDataExtractor.extract_teammates(match_details, user_steam_id)
        if teammates:
            logger.info(f"Found {len(teammates)} teammates for user {user_steam_id} in match {match_id}")
            store_teammate_relationships(db, user_id, teammates)

    except Exception as e:
        logger.error(f"Error processing players for match {match_id}: {e}")
        raise


def store_teammate_relationships(db: Session, user_id: int, teammate_steam_ids: list):
    """Store or update teammate relationships"""
    from app.models.teammate import UserTeammate
    from datetime import datetime

    for teammate_steam_id in teammate_steam_ids:
        try:
            # Check if relationship already exists
            existing = db.query(UserTeammate).filter(
                UserTeammate.user_id == user_id,
                UserTeammate.player_steam_id == teammate_steam_id
            ).first()

            if existing:
                # Update existing relationship
                existing.matches_together += 1
                existing.last_seen = datetime.utcnow()
                logger.debug(f"Updated teammate relationship: user {user_id} + {teammate_steam_id} ({existing.matches_together} matches)")
            else:
                # Create new relationship
                teammate = UserTeammate(
                    user_id=user_id,
                    player_steam_id=teammate_steam_id,
                    matches_together=1,
                    first_seen=datetime.utcnow(),
                    last_seen=datetime.utcnow(),
                    relationship_type='teammate'
                )
                db.add(teammate)
                logger.debug(f"Created new teammate relationship: user {user_id} + {teammate_steam_id}")

            db.commit()
        except Exception as e:
            logger.error(f"Error storing teammate relationship for {teammate_steam_id}: {e}")
            db.rollback()


@celery_app.task(bind=True)
def fetch_new_matches_for_all_users(self):
    """Scheduled task to fetch new matches for all active users"""
    db = SessionLocal()
    try:
        # Get all users with sync enabled
        active_users = db.query(User).filter(User.sync_enabled == True).all()

        logger.info(f"Starting match sync for {len(active_users)} users")

        for user in active_users:
            try:
                # Trigger individual user match sync
                fetch_user_matches.delay(user.user_id)
            except Exception as e:
                logger.error(f"Failed to queue match sync for user {user.user_id}: {e}")

        return {
            "status": "completed",
            "users_processed": len(active_users)
        }

    except Exception as e:
        logger.error(f"Error in fetch_new_matches_for_all_users: {e}")
        self.retry(countdown=300, max_retries=3)  # Retry after 5 minutes
    finally:
        db.close()


@celery_app.task(bind=True)
def fetch_user_matches(self, user_id: int, limit: int = 10):
    """Fetch recent matches for a specific user"""
    db = SessionLocal()
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}

        if not user.sync_enabled:
            logger.info(f"Sync disabled for user {user_id}")
            return {"status": "skipped", "message": "Sync disabled"}

        logger.info(f"Fetching matches for user {user_id} (Steam ID: {user.steam_id})")

        # Fetch matches from Leetify API using asyncio
        matches_found = 0
        new_matches = 0

        async def fetch_matches_async():
            nonlocal matches_found, new_matches
            async with get_leetify_api_client() as leetify_api:
                try:
                    # Get recent games from Leetify API
                    games = await leetify_api.get_recent_games(user.steam_id, limit=10)
                    matches_found = len(games)
                    logger.info(f"Found {matches_found} matches for user {user_id}")

                    for game in games:
                        # Extract match data
                        match_data = LeetifyDataExtractor.extract_match_data(game)
                        match_id = match_data["match_id"]

                        if not match_id:
                            logger.warning(f"Skipping match with missing ID for user {user_id}")
                            continue

                        # Check if match already exists
                        existing_match = get_match_by_id(db, match_id)
                        if existing_match:
                            logger.debug(f"Match {match_id} already exists, skipping")
                            continue

                        # Get detailed match information
                        match_details = await leetify_api.get_game_details(match_id, user.steam_id)
                        if not match_details:
                            logger.warning(f"Could not get details for match {match_id}")
                            continue

                        # Create match record
                        try:
                            # Update match_data with additional details and user info
                            match_data.update({
                                "user_id": user_id,
                                "match_date": match_data.get("started_at") or datetime.utcnow(),
                                "map": match_data.get("map_name"),
                                "leetify_match_id": match_id,
                                "processed": False
                            })

                            # Remove fields that don't exist in the Match model
                            db_match_data = {
                                "match_id": match_id,
                                "user_id": match_data["user_id"],
                                "match_date": match_data["match_date"],
                                "map": match_data.get("map"),
                                "score_team1": match_data.get("score_team1"),
                                "score_team2": match_data.get("score_team2"),
                                "leetify_match_id": match_data["leetify_match_id"],
                                "processed": match_data["processed"]
                            }

                            created_match = create_match(db, db_match_data)
                            new_matches += 1
                            logger.info(f"Created match {match_id} for user {user_id}")

                            # Process players in this match
                            await process_match_players_async(db, match_details, match_id, user.steam_id)

                        except Exception as e:
                            logger.error(f"Failed to create match {match_id}: {e}")
                            db.rollback()

                except Exception as e:
                    logger.error(f"Failed to fetch matches from Leetify API: {e}")
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


@celery_app.task(bind=True)
def process_match_data(self, match_id: str, user_id: int):
    """Process individual match data and extract player information"""
    db = SessionLocal()
    try:
        logger.info(f"Processing match {match_id} for user {user_id}")

        # TODO: Implement match processing logic
        # 1. Parse match data
        # 2. Extract player information
        # 3. Create/update player records
        # 4. Update user-teammate relationships
        # 5. Trigger player analysis for new players

        return {
            "status": "completed",
            "match_id": match_id,
            "players_processed": 0  # Placeholder
        }

    except Exception as e:
        logger.error(f"Error processing match {match_id}: {e}")
        self.retry(countdown=30, max_retries=2)
    finally:
        db.close()