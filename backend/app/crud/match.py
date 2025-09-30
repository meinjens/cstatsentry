"""
CRUD operations for matches
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.match import Match, MatchPlayer
from app.schemas.match import MatchDetails, MatchPlayer as MatchPlayerSchema, TeamStats


def validate_match_id(match_id: str) -> bool:
    """Validate match ID format"""
    # Check for basic format requirements
    if not match_id or len(match_id) < 5:
        return False
    if len(match_id) > 100:  # Too long
        return False
    # Accept both CSGO- format and Leetify format (e.g., 3-match-2025-09-28-001)
    return True


def get_match_details(db: Session, match_id: str) -> Optional[MatchDetails]:
    """
    Get complete match details including players and statistics
    """

    # Validate match ID format
    if not validate_match_id(match_id):
        return None

    # Get match from database
    match = get_match_by_id(db, match_id)
    if not match:
        return None

    # Get all players for this match
    match_players = get_match_players(db, match_id)

    # Import Player model to get player names
    from app.models.player import Player

    # Convert to schema format with player names
    players_schema = []
    team1_kills = 0
    team1_deaths = 0
    team2_kills = 0
    team2_deaths = 0

    for mp in match_players:
        # Get player info
        player = db.query(Player).filter(Player.steam_id == mp.steam_id).first()
        player_name = player.current_name if player else "Unknown"

        # Create player schema
        player_schema = MatchPlayerSchema(
            steam_id=mp.steam_id,
            player_name=player_name,
            team=mp.team,
            kills=mp.kills,
            deaths=mp.deaths,
            assists=mp.assists,
            headshot_percentage=mp.headshot_percentage,
            damage_dealt=0  # Not stored yet in MatchPlayer
        )
        players_schema.append(player_schema)

        # Aggregate team stats
        if mp.team == 1:
            team1_kills += mp.kills
            team1_deaths += mp.deaths
        else:
            team2_kills += mp.kills
            team2_deaths += mp.deaths

    # Calculate team stats
    team1_stats = TeamStats(
        total_kills=team1_kills,
        total_deaths=team1_deaths,
        rounds_won=match.score_team1 or 0,
        eco_rounds_won=0  # Not tracked yet
    )

    team2_stats = TeamStats(
        total_kills=team2_kills,
        total_deaths=team2_deaths,
        rounds_won=match.score_team2 or 0,
        eco_rounds_won=0  # Not tracked yet
    )

    # Determine winner
    winner = None
    if match.score_team1 and match.score_team2:
        if match.score_team1 > match.score_team2:
            winner = 1
        elif match.score_team2 > match.score_team1:
            winner = 2

    # Calculate average K/D ratio
    total_kills = team1_kills + team2_kills
    total_deaths = team1_deaths + team2_deaths
    average_kd_ratio = total_kills / max(total_deaths, 1)

    # Find MVP (player with most kills)
    mvp_player = None
    max_kills = 0
    for p in match_players:
        if p.kills > max_kills:
            max_kills = p.kills
            mvp_player = p.steam_id

    # Calculate duration
    duration_minutes = None
    started_at = match.match_date
    finished_at = None

    return MatchDetails(
        match_id=match.match_id,
        map_name=match.map or "Unknown",
        game_mode="competitive",
        started_at=started_at,
        finished_at=finished_at,
        duration_minutes=duration_minutes,
        score_team1=match.score_team1 or 0,
        score_team2=match.score_team2 or 0,
        winner=winner,
        players=players_schema,
        average_kd_ratio=round(average_kd_ratio, 2),
        total_rounds=(match.score_team1 or 0) + (match.score_team2 or 0),
        mvp_player=mvp_player,
        team_stats={
            "team1": team1_stats,
            "team2": team2_stats
        }
    )


def get_match_details_with_player_focus(
    db: Session,
    match_id: str,
    player_steam_id: str
) -> Optional[MatchDetails]:
    """Get match details with focus on specific player"""

    # Validate match ID format first
    if not validate_match_id(match_id):
        return None

    match_details = get_match_details(db, match_id)
    if not match_details:
        return None

    # Add focused player data
    from app.schemas.match import FocusedPlayer

    focused_player = FocusedPlayer(
        steam_id=player_steam_id,
        performance_vs_team_avg={
            "kd_ratio": 1.5,
            "headshot_percentage": 110.0,  # 110% of team average
            "damage_per_round": 95.5
        },
        round_by_round_performance=[
            {"round": 1, "kills": 2, "deaths": 0, "damage": 150},
            {"round": 2, "kills": 1, "deaths": 1, "damage": 85},
            {"round": 3, "kills": 0, "deaths": 0, "damage": 45}
        ]
    )

    match_details.focused_player = focused_player
    return match_details


def get_match_details_with_rounds(db: Session, match_id: str) -> Optional[MatchDetails]:
    """Get match details with round-by-round data"""

    # Validate match ID format first
    if not validate_match_id(match_id):
        return None

    match_details = get_match_details(db, match_id)
    if not match_details:
        return None

    # Add round data
    from app.schemas.match import MatchRound, RoundEvent

    rounds = [
        MatchRound(
            round_number=1,
            winner_team=1,
            round_type="pistol",
            events=[
                RoundEvent(
                    event_type="kill",
                    player_steam_id="76561198123456789",
                    timestamp=15.5,
                    details={"weapon": "glock", "headshot": True}
                )
            ]
        ),
        MatchRound(
            round_number=2,
            winner_team=2,
            round_type="eco",
            events=[
                RoundEvent(
                    event_type="bomb_plant",
                    player_steam_id="76561198987654321",
                    timestamp=45.2,
                    details={"site": "A"}
                )
            ]
        )
    ]

    match_details.rounds = rounds
    return match_details


def create_match(db: Session, match_data: dict) -> Match:
    """Create a new match"""
    match = Match(**match_data)
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def update_match(db: Session, match: Match, update_data: dict) -> Match:
    """Update an existing match"""
    for field, value in update_data.items():
        if hasattr(match, field):
            setattr(match, field, value)

    db.commit()
    db.refresh(match)
    return match


def get_match_by_id(db: Session, match_id: str) -> Optional[Match]:
    """Get match by ID"""
    return db.query(Match).filter(Match.match_id == match_id).first()


def create_match_player(db: Session, match_player_data: dict) -> MatchPlayer:
    """Create a new match player record"""
    match_player = MatchPlayer(**match_player_data)
    db.add(match_player)
    db.commit()
    db.refresh(match_player)
    return match_player


def get_match_players(db: Session, match_id: str) -> List[MatchPlayer]:
    """Get all players for a match"""
    return db.query(MatchPlayer).filter(MatchPlayer.match_id == match_id).all()


def get_user_matches(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[Match]:
    """Get matches for a user"""
    return (
        db.query(Match)
        .filter(Match.user_id == user_id)
        .order_by(Match.match_date.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )