from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.player import Player, PlayerBan, PlayerAnalysis
from app.models.match import MatchPlayer, Match
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerStats


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


def get_player_stats(db: Session, steam_id: str) -> Optional[PlayerStats]:
    """Get player statistics aggregated from match data"""
    # Check if player exists
    player = get_player_by_steam_id(db, steam_id)
    if not player:
        return None

    # Aggregate basic stats from match_players table
    stats_query = (
        db.query(
            func.count(MatchPlayer.match_id).label('total_matches'),
            func.sum(MatchPlayer.kills).label('total_kills'),
            func.sum(MatchPlayer.deaths).label('total_deaths'),
            func.avg(MatchPlayer.headshot_percentage).label('avg_headshot_percentage')
        )
        .filter(MatchPlayer.steam_id == steam_id)
        .first()
    )

    # Handle case where no matches exist
    if not stats_query or stats_query.total_matches == 0:
        return PlayerStats(
            steam_id=steam_id,
            total_matches=0,
            total_kills=0,
            total_deaths=0,
            kd_ratio=0.0,
            headshot_percentage=0.0,
            average_damage_per_round=0.0,
            wins=0,
            losses=0,
            win_rate=0.0
        )

    total_matches = stats_query.total_matches or 0
    total_kills = stats_query.total_kills or 0
    total_deaths = stats_query.total_deaths or 0
    avg_headshot_percentage = float(stats_query.avg_headshot_percentage or 0.0)

    # For now, use placeholder values for wins/losses (would need more complex query)
    # In a real implementation, we'd need to determine wins based on team and scores
    wins = 0
    losses = 0

    # Calculate derived stats
    kd_ratio = float(total_kills / max(total_deaths, 1))  # Avoid division by zero
    win_rate = 0.0

    # Placeholder for average damage per round (would need more detailed match data)
    average_damage_per_round = 0.0

    return PlayerStats(
        steam_id=steam_id,
        total_matches=total_matches,
        total_kills=total_kills,
        total_deaths=total_deaths,
        kd_ratio=kd_ratio,
        headshot_percentage=avg_headshot_percentage,
        average_damage_per_round=average_damage_per_round,
        wins=wins,
        losses=losses,
        win_rate=win_rate
    )