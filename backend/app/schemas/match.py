"""
Match-related Pydantic schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class MatchPlayer(BaseModel):
    """Player performance in a match"""
    steam_id: str
    player_name: Optional[str] = None
    team: int
    kills: int
    deaths: int
    assists: int
    headshot_percentage: float = 0.0
    damage_dealt: int = 0

    class Config:
        from_attributes = True


class TeamStats(BaseModel):
    """Team-level statistics for a match"""
    total_kills: int
    total_deaths: int
    rounds_won: int
    eco_rounds_won: int = 0

    class Config:
        from_attributes = True


class FocusedPlayer(BaseModel):
    """Player-specific performance metrics"""
    steam_id: str
    performance_vs_team_avg: Dict[str, float]
    round_by_round_performance: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class RoundEvent(BaseModel):
    """Event that occurred during a round"""
    event_type: str
    player_steam_id: str
    timestamp: float
    details: Dict[str, Any]

    class Config:
        from_attributes = True


class MatchRound(BaseModel):
    """Round-by-round data"""
    round_number: int
    winner_team: int
    round_type: str  # eco, anti-eco, full-buy
    events: List[RoundEvent]

    class Config:
        from_attributes = True


class MatchDetails(BaseModel):
    """Complete match details response"""
    match_id: str
    map_name: str
    game_mode: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    score_team1: int
    score_team2: int
    winner: Optional[int] = None
    players: List[MatchPlayer]

    # Performance metrics
    average_kd_ratio: float
    total_rounds: int
    mvp_player: Optional[str] = None

    # Team statistics
    team_stats: Dict[str, TeamStats]

    # Optional fields for detailed requests
    focused_player: Optional[FocusedPlayer] = None
    rounds: Optional[List[MatchRound]] = None

    class Config:
        from_attributes = True