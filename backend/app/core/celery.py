from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "statsentry",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.match_sync",
        "app.tasks.player_analysis",
        "app.tasks.steam_data_update"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Schedule configuration
celery_app.conf.beat_schedule = {
    "fetch-new-matches": {
        "task": "app.tasks.match_sync.fetch_new_matches_for_all_users",
        "schedule": 30.0 * 60,  # Every 30 minutes
    },
    "update-ban-status": {
        "task": "app.tasks.steam_data_update.update_ban_status_batch",
        "schedule": 24.0 * 60 * 60,  # Daily
    },
    "cleanup-old-data": {
        "task": "app.tasks.steam_data_update.cleanup_old_data",
        "schedule": 24.0 * 60 * 60,  # Daily
    },
}