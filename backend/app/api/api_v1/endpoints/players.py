from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.player import Player as PlayerSchema, PlayerWithAnalysis, PlayerAnalysis
from app.crud.player import (
    get_player_by_steam_id,
    get_player_analyses,
    get_latest_player_analysis,
    get_player_ban_info
)
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


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