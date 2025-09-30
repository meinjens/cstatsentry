"""
Base interface for match data providers (Leetify, Steam, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MatchData:
    """Standardized match data structure"""
    match_id: str
    map_name: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    score_team1: int = 0
    score_team2: int = 0
    game_type: str = "competitive"
    demo_url: Optional[str] = None
    sharecode: Optional[str] = None  # CS2 match sharecode (for Steam API)
    raw_data: Optional[Dict[str, Any]] = None  # Provider-specific data


@dataclass
class PlayerPerformance:
    """Standardized player performance data"""
    steam_id: str
    player_name: str
    team: int  # 1 or 2
    kills: int
    deaths: int
    assists: int
    adr: float = 0.0
    rating: float = 0.0
    headshots: int = 0
    mvps: int = 0


@dataclass
class MatchDetails:
    """Complete match details with player data"""
    match_data: MatchData
    players: List[PlayerPerformance]


class MatchDataProvider(ABC):
    """Abstract base class for match data providers"""

    @abstractmethod
    async def authenticate(self, steam_id: str) -> bool:
        """
        Authenticate with the provider
        Returns True if successful
        """
        pass

    @abstractmethod
    async def get_recent_matches(self, steam_id: str, limit: int = 10) -> List[MatchData]:
        """
        Get list of recent matches for a player
        """
        pass

    @abstractmethod
    async def get_match_details(self, match_id: str, steam_id: str) -> Optional[MatchDetails]:
        """
        Get detailed information about a specific match
        """
        pass

    @abstractmethod
    async def close(self):
        """
        Clean up resources (close HTTP clients, etc.)
        """
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider"""
        pass