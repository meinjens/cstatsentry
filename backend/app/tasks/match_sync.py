from celery import current_task
from app.core.celery import celery_app
from app.db.session import SessionLocal
from app.crud.user import get_user_by_id
from app.models.user import User
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


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

        # TODO: Implement Leetify API integration
        # For now, return placeholder

        # Update last_sync timestamp
        from datetime import datetime
        user.last_sync = datetime.utcnow()
        db.commit()

        return {
            "status": "completed",
            "user_id": user_id,
            "matches_found": 0,  # Placeholder
            "new_matches": 0     # Placeholder
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