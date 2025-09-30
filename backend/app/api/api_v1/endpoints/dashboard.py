from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.match import Match
from app.models.player import Player, PlayerAnalysis

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get dashboard overview statistics"""

    # Count total matches for this user
    total_matches = db.query(Match).filter(Match.user_id == current_user.user_id).count()

    # Count unique players that have been analyzed (have at least one analysis)
    total_players_analyzed = db.query(PlayerAnalysis.steam_id).distinct().count()

    # Count suspicious players (latest analysis with suspicion_score >= 60)
    # Get latest analysis per player with subquery
    from sqlalchemy import and_
    subquery = (
        db.query(
            PlayerAnalysis.steam_id,
            func.max(PlayerAnalysis.analyzed_at).label('max_date')
        )
        .group_by(PlayerAnalysis.steam_id)
        .subquery()
    )

    suspicious_players = db.query(PlayerAnalysis).join(
        subquery,
        and_(
            PlayerAnalysis.steam_id == subquery.c.steam_id,
            PlayerAnalysis.analyzed_at == subquery.c.max_date
        )
    ).filter(PlayerAnalysis.suspicion_score >= 60).count()

    # Count high risk players (latest analysis with suspicion_score >= 80)
    high_risk_players = db.query(PlayerAnalysis).join(
        subquery,
        and_(
            PlayerAnalysis.steam_id == subquery.c.steam_id,
            PlayerAnalysis.analyzed_at == subquery.c.max_date
        )
    ).filter(PlayerAnalysis.suspicion_score >= 80).count()

    # Count new detections today (analyses with suspicion_score >= 60 created today)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    new_detections_today = db.query(PlayerAnalysis).filter(
        PlayerAnalysis.suspicion_score >= 60,
        PlayerAnalysis.analyzed_at >= today_start
    ).count()

    return {
        "total_matches": total_matches,
        "total_players_analyzed": total_players_analyzed,
        "suspicious_players": suspicious_players,
        "high_risk_players": high_risk_players,
        "new_detections_today": new_detections_today,
        "last_sync": current_user.last_sync
    }


@router.get("/recent")
async def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get recent suspicious activities"""
    # TODO: Implement recent activity feed
    return {
        "recent_analyses": [],
        "new_flags": [],
        "updated_players": []
    }


@router.get("/statistics")
async def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed user statistics and trends"""
    # TODO: Implement detailed statistics
    return {
        "matches_by_month": [],
        "suspicion_score_distribution": {},
        "detection_trends": [],
        "most_common_flags": []
    }