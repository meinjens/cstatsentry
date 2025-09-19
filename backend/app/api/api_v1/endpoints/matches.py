from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def get_user_matches(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's match history"""
    # TODO: Implement match retrieval from database
    return {
        "matches": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.get("/{match_id}")
async def get_match_details(
    match_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific match details"""
    # TODO: Implement match details retrieval
    raise HTTPException(status_code=404, detail="Match not found")


@router.post("/sync")
async def trigger_match_sync(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger manual match synchronization"""
    # TODO: Trigger Celery task for match sync
    return {
        "message": "Match synchronization started",
        "user_id": current_user.user_id,
        "status": "queued"
    }


@router.get("/sync/status")
async def get_sync_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check synchronization status"""
    # TODO: Check Celery task status
    return {
        "status": "idle",  # idle, running, completed, failed
        "last_sync": current_user.last_sync,
        "sync_enabled": current_user.sync_enabled
    }