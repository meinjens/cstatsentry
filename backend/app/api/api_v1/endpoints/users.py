from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import User as UserSchema, UserUpdate, TeammateSchema
from app.crud.user import update_user
from app.api.deps import get_current_user
from app.models.user import User
from app.models.teammate import UserTeammate
from app.models.player import Player

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    update_data = user_update.dict(exclude_unset=True)
    updated_user = update_user(db, current_user, update_data)
    return updated_user


@router.get("/me/teammates", response_model=List[TeammateSchema])
async def get_user_teammates(
    limit: int = Query(50, ge=1, le=100),
    min_matches: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's teammates sorted by matches played together"""

    # Query teammates with player info
    teammates = (
        db.query(UserTeammate, Player)
        .join(Player, UserTeammate.player_steam_id == Player.steam_id)
        .filter(
            UserTeammate.user_id == current_user.user_id,
            UserTeammate.matches_together >= min_matches
        )
        .order_by(UserTeammate.matches_together.desc())
        .limit(limit)
        .all()
    )

    # Convert to schema
    result = []
    for teammate_rel, player in teammates:
        result.append(TeammateSchema(
            player_steam_id=player.steam_id,
            player_name=player.current_name,
            matches_together=teammate_rel.matches_together,
            first_seen=teammate_rel.first_seen,
            last_seen=teammate_rel.last_seen,
            relationship_type=teammate_rel.relationship_type
        ))

    return result