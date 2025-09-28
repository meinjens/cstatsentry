from celery import current_task
from app.core.celery import celery_app
from app.db.session import SessionLocal
from app.models.player import Player, PlayerBan
from app.crud.player import create_or_update_player_ban
from app.services.steam_api import get_steam_api_client, SteamDataExtractor
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def update_ban_status_batch(self, batch_size: int = 100):
    """Weekly task to update VAC ban status for all players"""
    db = SessionLocal()
    try:
        # Get all players that need ban status update
        cutoff_date = datetime.utcnow() - timedelta(days=7)

        players_to_update = (
            db.query(Player.steam_id)
            .outerjoin(PlayerBan)
            .filter(
                (PlayerBan.updated_at.is_(None)) |
                (PlayerBan.updated_at < cutoff_date)
            )
            .limit(batch_size * 10)  # Get more than we need for batching
            .all()
        )

        if not players_to_update:
            logger.info("No players need ban status update")
            return {"status": "completed", "players_updated": 0}

        steam_ids = [p.steam_id for p in players_to_update]
        updated_count = 0

        # Process in batches of 100 (Steam API limit)
        import asyncio

        async def process_batch(batch_ids):
            async with get_steam_api_client() as steam_api:
                ban_data = await steam_api.get_player_bans(batch_ids)
                return ban_data

        for i in range(0, len(steam_ids), batch_size):
            batch_ids = steam_ids[i:i + batch_size]

            try:
                ban_data = asyncio.run(process_batch(batch_ids))

                if ban_data.get("players"):
                    for ban_info in ban_data["players"]:
                        extracted_data = SteamDataExtractor.extract_ban_data(ban_info)
                        create_or_update_player_ban(db, extracted_data)
                        updated_count += 1

                # Update task progress
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + len(batch_ids),
                        "total": len(steam_ids),
                        "status": f"Updated {updated_count} players"
                    }
                )

            except Exception as e:
                logger.error(f"Error updating ban status for batch {i}: {e}")

        logger.info(f"Updated ban status for {updated_count} players")

        return {
            "status": "completed",
            "players_updated": updated_count,
            "total_checked": len(steam_ids)
        }

    except Exception as e:
        logger.error(f"Error in update_ban_status_batch: {e}")
        self.retry(countdown=300, max_retries=3)
    finally:
        db.close()


@celery_app.task(bind=True)
def cleanup_old_data(self):
    """Daily cleanup task to remove old cache entries and temporary data"""
    db = SessionLocal()
    try:
        # TODO: Implement cleanup logic
        # - Remove old analysis records (keep last 10 per player)
        # - Clean up old cache entries
        # - Remove orphaned records

        logger.info("Starting data cleanup")

        # Placeholder cleanup
        cleaned_items = 0

        return {
            "status": "completed",
            "items_cleaned": cleaned_items
        }

    except Exception as e:
        logger.error(f"Error in cleanup_old_data: {e}")
        self.retry(countdown=300, max_retries=2)
    finally:
        db.close()


@celery_app.task(bind=True)
def update_player_profiles_batch(self, batch_size: int = 50):
    """Update player profiles that are outdated"""
    db = SessionLocal()
    try:
        # Get players with outdated profile data (older than 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)

        players_to_update = (
            db.query(Player.steam_id)
            .filter(
                (Player.profile_updated.is_(None)) |
                (Player.profile_updated < cutoff_date)
            )
            .limit(batch_size * 5)  # Get more for batching
            .all()
        )

        if not players_to_update:
            logger.info("No player profiles need update")
            return {"status": "completed", "profiles_updated": 0}

        steam_ids = [p.steam_id for p in players_to_update]
        updated_count = 0

        # Process in batches
        import asyncio

        async def process_profile_batch(batch_ids):
            async with get_steam_api_client() as steam_api:
                summary_data = await steam_api.get_player_summaries(batch_ids)
                return summary_data

        for i in range(0, len(steam_ids), batch_size):
            batch_ids = steam_ids[i:i + batch_size]

            try:
                summary_data = asyncio.run(process_profile_batch(batch_ids))

                if summary_data.get("response", {}).get("players"):
                    for player_info in summary_data["response"]["players"]:
                        extracted_data = SteamDataExtractor.extract_player_data(player_info)
                        extracted_data["profile_updated"] = datetime.utcnow()

                        # Update player in database
                        player = db.query(Player).filter(
                            Player.steam_id == extracted_data["steam_id"]
                        ).first()

                        if player:
                            for field, value in extracted_data.items():
                                if hasattr(player, field):
                                    setattr(player, field, value)

                            updated_count += 1

                    db.commit()

                # Update task progress
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + len(batch_ids),
                        "total": len(steam_ids),
                        "status": f"Updated {updated_count} profiles"
                    }
                )

            except Exception as e:
                logger.error(f"Error updating profiles for batch {i}: {e}")

        logger.info(f"Updated {updated_count} player profiles")

        return {
            "status": "completed",
            "profiles_updated": updated_count,
            "total_checked": len(steam_ids)
        }

    except Exception as e:
        logger.error(f"Error in update_player_profiles_batch: {e}")
        self.retry(countdown=300, max_retries=2)
    finally:
        db.close()