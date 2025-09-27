from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class PlayerBase(BaseModel):
    steam_id: str
    current_name: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None


class PlayerCreate(PlayerBase):
    previous_names: Optional[List[str]] = []
    account_created: Optional[datetime] = None
    last_logoff: Optional[datetime] = None
    profile_state: Optional[int] = None
    visibility_state: Optional[int] = None
    country_code: Optional[str] = None
    cs2_hours: int = 0
    total_games_owned: int = 0


class PlayerUpdate(BaseModel):
    current_name: Optional[str] = None
    previous_names: Optional[List[str]] = None
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None
    account_created: Optional[datetime] = None
    last_logoff: Optional[datetime] = None
    profile_state: Optional[int] = None
    visibility_state: Optional[int] = None
    country_code: Optional[str] = None
    cs2_hours: Optional[int] = None
    total_games_owned: Optional[int] = None


class Player(PlayerBase):
    previous_names: Optional[List[str]] = []
    account_created: Optional[datetime] = None
    last_logoff: Optional[datetime] = None
    profile_state: Optional[int] = None
    visibility_state: Optional[int] = None
    country_code: Optional[str] = None
    cs2_hours: int = 0
    total_games_owned: int = 0
    profile_updated: Optional[datetime] = None
    stats_updated: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PlayerBanBase(BaseModel):
    steam_id: str
    community_banned: bool = False
    vac_banned: bool = False
    number_of_vac_bans: int = 0
    days_since_last_ban: int = 0
    number_of_game_bans: int = 0
    economy_ban: str = "none"


class PlayerBan(PlayerBanBase):
    updated_at: datetime

    class Config:
        from_attributes = True


class PlayerAnalysisBase(BaseModel):
    steam_id: str
    suspicion_score: int
    flags: Dict[str, Any]
    confidence_level: Decimal
    analysis_version: str
    notes: Optional[str] = None


class PlayerAnalysisCreate(PlayerAnalysisBase):
    analyzed_by: int


class PlayerAnalysis(PlayerAnalysisBase):
    analysis_id: int
    analyzed_by: int
    analyzed_at: datetime

    class Config:
        from_attributes = True


class PlayerStats(BaseModel):
    """Player game statistics"""
    steam_id: str
    total_matches: int
    total_kills: int
    total_deaths: int
    kd_ratio: float
    headshot_percentage: float
    average_damage_per_round: float
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0

    class Config:
        from_attributes = True


class PlayerWithAnalysis(Player):
    """Player with latest analysis data"""
    latest_analysis: Optional[PlayerAnalysis] = None
    ban_info: Optional[PlayerBan] = None