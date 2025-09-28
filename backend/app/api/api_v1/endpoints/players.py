from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import get_db
from app.schemas.player import Player as PlayerSchema, PlayerWithAnalysis, PlayerAnalysis, PlayerStats
from app.crud.player import (
    get_player_by_steam_id,
    get_player_analyses,
    get_latest_player_analysis,
    get_player_ban_info,
    get_player_stats,
    update_player
)
from app.api.deps import get_current_user, security
from app.models.user import User
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter()


@router.get("/debug/auth")
async def debug_players_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Debug authentication for players endpoints"""
    from app.core.security import decode_token
    from datetime import datetime

    if not credentials:
        return {
            "error": "No Authorization header found",
            "message": "Frontend is not sending the token",
            "expected_header": "Authorization: Bearer <token>"
        }

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        return {
            "error": "Invalid token",
            "token_preview": f"{token[:10]}...{token[-10:]}",
            "message": "Token is malformed or expired"
        }

    exp_timestamp = payload.get("exp")
    exp_datetime = datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None
    time_until_expiry = (exp_datetime - datetime.now()).total_seconds() if exp_datetime else None

    return {
        "success": True,
        "message": "Token is valid and properly sent",
        "steam_id": payload.get("sub"),
        "expires_at": exp_datetime.isoformat() if exp_datetime else None,
        "expires_in_seconds": time_until_expiry,
        "expires_in_minutes": time_until_expiry / 60 if time_until_expiry else None,
        "is_expired": time_until_expiry < 0 if time_until_expiry else None
    }


@router.get("/{steam_id}", response_model=PlayerWithAnalysis)
async def get_player(
    steam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get player details with latest analysis"""
    player = get_player_by_steam_id(db, steam_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Get latest analysis and ban info
    latest_analysis = get_latest_player_analysis(db, steam_id)
    ban_info = get_player_ban_info(db, steam_id)

    # Convert to response model
    player_data = PlayerWithAnalysis.from_orm(player)
    player_data.latest_analysis = latest_analysis
    player_data.ban_info = ban_info

    return player_data


@router.get("/{steam_id}/stats", response_model=PlayerStats)
async def get_player_stats_endpoint(
    steam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get player game statistics"""
    player = get_player_by_steam_id(db, steam_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    stats = get_player_stats(db, steam_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Player not found")

    return stats


@router.get("/{steam_id}/analysis", response_model=List[PlayerAnalysis])
async def get_player_analysis_history(
    steam_id: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get player analysis history"""
    player = get_player_by_steam_id(db, steam_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    analyses = get_player_analyses(db, steam_id, limit)
    return analyses


@router.post("/{steam_id}/analyze")
async def trigger_player_analysis(
    steam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger manual analysis for a player"""
    player = get_player_by_steam_id(db, steam_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # TODO: Trigger Celery task for player analysis
    # For now, return a placeholder response
    return {
        "message": f"Analysis triggered for player {steam_id}",
        "status": "queued"
    }


@router.get("/", response_model=List[PlayerSchema])
@router.get("", response_model=List[PlayerSchema])  # Support both with and without trailing slash
async def get_suspicious_players(
    min_suspicion_score: int = Query(60, ge=0, le=100),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of suspicious players"""
    # TODO: Implement query for suspicious players
    # This would join players with their latest analysis
    # and filter by suspicion score
    return []


@router.post("/{steam_id}/update")
async def update_player_profile(
    steam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update player profile from Steam API"""
    player = get_player_by_steam_id(db, steam_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Check rate limiting (max one update per hour per player)
    if player.profile_updated:
        time_since_last_update = datetime.now() - player.profile_updated
        if time_since_last_update < timedelta(hours=1):
            # Calculate seconds until next allowed update
            retry_after = int((timedelta(hours=1) - time_since_last_update).total_seconds())
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Profile update rate limited",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )

    # Mock update (in real implementation, would call Steam API)
    update_data = {
        "profile_updated": datetime.now(),
        "current_name": f"Updated_{player.current_name}",
    }

    updated_fields = ["profile_updated", "current_name"]

    # Update player
    updated_player = update_player(db, player, update_data)

    return {
        "steam_id": steam_id,
        "updated_fields": updated_fields,
        "updated_at": updated_player.profile_updated.isoformat()
    }