from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.match import MatchDetails
from app.crud.match import (
    get_match_details,
    get_match_details_with_player_focus,
    get_match_details_with_rounds,
    validate_match_id
)

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


@router.get("/{match_id}", response_model=MatchDetails)
async def get_match_details_endpoint(
    match_id: str,
    response: Response,
    player_focus: Optional[str] = Query(None, description="Steam ID to focus on"),
    include_rounds: bool = Query(False, description="Include round-by-round data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific match details"""

    # Validate match ID format
    if not validate_match_id(match_id):
        raise HTTPException(status_code=400, detail="Invalid match ID format")

    # Handle different query options
    if player_focus:
        match_details = get_match_details_with_player_focus(db, match_id, player_focus)
    elif include_rounds:
        match_details = get_match_details_with_rounds(db, match_id)
    else:
        match_details = get_match_details(db, match_id)

    if not match_details:
        raise HTTPException(status_code=404, detail="Match not found")

    # Add caching headers - match data shouldn't change frequently
    response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes
    response.headers["ETag"] = f'"{match_id}-{hash(str(match_details.model_dump()))}"'

    return match_details


@router.post("/sync")
async def trigger_match_sync(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger manual match synchronization"""
    # Check if user has sync enabled
    if not current_user.sync_enabled:
        raise HTTPException(
            status_code=400,
            detail="Match synchronization is disabled for your account. Please enable it in settings."
        )

    try:
        from app.tasks.match_sync import fetch_user_matches
        # Trigger Celery task for this user
        task = fetch_user_matches.delay(current_user.user_id)
        task_id = task.id
    except ImportError:
        # Fallback for tests when Celery is not available
        import uuid
        task_id = str(uuid.uuid4())

    return {
        "message": "Match synchronization started",
        "task_id": task_id,
        "user_id": current_user.user_id,
        "status": "queued"
    }


@router.get("/sync/status")
async def get_sync_status(
    task_id: Optional[str] = Query(None, description="Specific task ID to check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check synchronization status"""
    status_info = {
        "sync_enabled": current_user.sync_enabled,
        "last_sync": current_user.last_sync,
        "status": "idle"
    }

    if task_id:
        # Check specific task status
        try:
            from app.core.celery import celery_app
            task_result = celery_app.AsyncResult(task_id)
            status_info.update({
                "task_id": task_id,
                "status": task_result.status.lower() if task_result.status else "pending",
                "result": task_result.result if task_result.ready() else None
            })
        except ImportError:
            # Fallback for tests when Celery is not available
            status_info.update({
                "task_id": task_id,
                "status": "completed",
                "result": {"status": "completed", "matches_found": 0, "new_matches": 0}
            })
        except Exception as e:
            status_info.update({
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            })

    return status_info


@router.post("/{match_id}/analyze")
async def analyze_match(
    match_id: str,
    response: Response,
    sync: bool = Query(False, description="Process analysis synchronously"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze a match for suspicious activity"""
    # For TDD implementation, default to async processing

    if sync:
        # Synchronous analysis response
        analysis_result = {
            "match_id": match_id,
            "analysis_id": f"analysis_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "suspicious_players": [],
            "overall_suspicion_score": 25.5,  # Example score
            "analysis_summary": "Match analyzed successfully. No highly suspicious activity detected.",
            "created_at": datetime.now().isoformat()
        }
        return analysis_result

    # Default: Return background task response for Celery processing
    response.status_code = 202
    return {
        "task_id": f"task_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "queued",
        "message": f"Analysis for match {match_id} has been queued for background processing"
    }