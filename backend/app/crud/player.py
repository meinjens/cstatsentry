from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.player import Player, PlayerBan, PlayerAnalysis
from app.schemas.player import PlayerCreate, PlayerUpdate


def get_player_by_steam_id(db: Session, steam_id: str) -> Optional[Player]:
    """Get player by Steam ID"""
    return db.query(Player).filter(Player.steam_id == steam_id).first()


def get_players_by_steam_ids(db: Session, steam_ids: List[str]) -> List[Player]:
    """Get multiple players by Steam IDs"""
    return db.query(Player).filter(Player.steam_id.in_(steam_ids)).all()


def create_player(db: Session, player_data: dict) -> Player:
    """Create a new player"""
    player = Player(**player_data)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


def update_player(db: Session, player: Player, update_data: dict) -> Player:
    """Update an existing player"""
    for field, value in update_data.items():
        if hasattr(player, field):
            setattr(player, field, value)

    db.commit()
    db.refresh(player)
    return player


def get_player_ban_info(db: Session, steam_id: str) -> Optional[PlayerBan]:
    """Get player ban information"""
    return db.query(PlayerBan).filter(PlayerBan.steam_id == steam_id).first()


def create_or_update_player_ban(db: Session, ban_data: dict) -> PlayerBan:
    """Create or update player ban information"""
    existing_ban = get_player_ban_info(db, ban_data["steam_id"])

    if existing_ban:
        # Update existing ban info
        for field, value in ban_data.items():
            if hasattr(existing_ban, field):
                setattr(existing_ban, field, value)
        db.commit()
        db.refresh(existing_ban)
        return existing_ban
    else:
        # Create new ban info
        new_ban = PlayerBan(**ban_data)
        db.add(new_ban)
        db.commit()
        db.refresh(new_ban)
        return new_ban


def get_player_analyses(db: Session, steam_id: str, limit: int = 10) -> List[PlayerAnalysis]:
    """Get player analysis history"""
    return (
        db.query(PlayerAnalysis)
        .filter(PlayerAnalysis.steam_id == steam_id)
        .order_by(PlayerAnalysis.analyzed_at.desc())
        .limit(limit)
        .all()
    )


def get_latest_player_analysis(db: Session, steam_id: str) -> Optional[PlayerAnalysis]:
    """Get latest player analysis"""
    return (
        db.query(PlayerAnalysis)
        .filter(PlayerAnalysis.steam_id == steam_id)
        .order_by(PlayerAnalysis.analyzed_at.desc())
        .first()
    )


def create_player_analysis(db: Session, analysis_data: dict) -> PlayerAnalysis:
    """Create a new player analysis"""
    analysis = PlayerAnalysis(**analysis_data)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis