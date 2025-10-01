import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.celery import celery_app
from app.crud.match import create_match_player
from app.crud.player import get_player_by_steam_id, create_player, update_player
from app.crud.user import get_user_by_id
from app.db.session import SessionLocal
from app.models.user import User
from app.services.leetify_api import LeetifyDataExtractor

logger = logging.getLogger(__name__)


async def process_match_players_async(db: Session, match_details: dict, match_id: str, user_steam_id: str, user_id: int):
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
    """
    Orchestrator task to fetch matches from all available sources in parallel

    This task coordinates multiple data sources (Leetify, Steam, etc.) and
    triggers them as separate async Celery tasks for parallel execution.
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

        logger.info(f"[Orchestrator] Starting multi-source match sync for user {user_id} (Steam ID: {user.steam_id})")

        # Import source-specific tasks
        from app.tasks.match_sync_leetify import sync_leetify_matches
        from app.tasks.match_sync_steam import sync_steam_matches

        # Trigger all sources in parallel using Celery's group
        from celery import group

        # Create task group for parallel execution
        job = group([
            sync_leetify_matches.s(user_id, user.steam_id, limit),
            sync_steam_matches.s(user_id, user.steam_id, limit),
            # Add more sources here as needed:
            # sync_faceit_matches.s(user_id, user.steam_id, limit),
            # sync_esea_matches.s(user_id, user.steam_id, limit),
        ])

        # Execute all tasks in parallel
        result = job.apply_async()

        # Wait for all tasks to complete (with timeout)
        results = result.get(timeout=300)  # 5 minute timeout

        # Aggregate results from all sources
        total_matches_found = 0
        total_new_matches = 0
        source_results = []

        for source_result in results:
            if source_result and source_result.get("status") == "completed":
                total_matches_found += source_result.get("matches_found", 0)
                total_new_matches += source_result.get("new_matches", 0)
                source_results.append({
                    "source": source_result.get("source"),
                    "matches_found": source_result.get("matches_found", 0),
                    "new_matches": source_result.get("new_matches", 0)
                })
                logger.info(f"[Orchestrator] {source_result.get('source')}: {source_result.get('new_matches', 0)} new matches")

        # Update last_sync timestamp
        user.last_sync = datetime.utcnow()
        db.commit()

        logger.info(f"[Orchestrator] Multi-source sync completed for Steam ID {user.steam_id}: {total_new_matches} new matches from {len(source_results)} sources")

        return {
            "status": "completed",
            "user_id": user_id,
            "total_matches_found": total_matches_found,
            "total_new_matches": total_new_matches,
            "sources": source_results
        }

    except Exception as e:
        logger.error(f"[Orchestrator] Error fetching matches for Steam ID {user.steam_id if 'user' in locals() else user_id}: {e}")
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