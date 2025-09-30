"""
Leetify API Adapter
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

import httpx

from app.core.config import settings
from .base import MatchDataProvider, MatchData, PlayerPerformance, MatchDetails

logger = logging.getLogger(__name__)


class LeetifyAdapter(MatchDataProvider):
    """Adapter for Leetify API"""

    def __init__(self):
        self.api_key = settings.LEETIFY_API_KEY
        self.base_url = getattr(settings, 'LEETIFY_API_URL', 'http://localhost:5001')
        self.client = httpx.AsyncClient(timeout=30.0)
        self._auth_token: Optional[str] = None

    @property
    def provider_name(self) -> str:
        return "Leetify"

    async def authenticate(self, steam_id: str) -> bool:
        """Get authentication token from Leetify API"""
        url = f"{self.base_url}/api/auth/token"

        try:
            response = await self.client.post(
                url,
                json={"steam_id": steam_id},
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()

            data = response.json()
            self._auth_token = data.get('access_token')
            return self._auth_token is not None

        except Exception as e:
            logger.error(f"[Leetify] Failed to authenticate: {e}")
            return False

    async def get_recent_matches(self, steam_id: str, limit: int = 10) -> List[MatchData]:
        """Get recent matches from Leetify API"""
        if not self._auth_token:
            if not await self.authenticate(steam_id):
                logger.error("[Leetify] Authentication failed")
                return []

        try:
            url = f"{self.base_url}/api/profile/{steam_id}/games"
            headers = {
                'Authorization': f'Bearer {self._auth_token}',
                'Content-Type': 'application/json'
            }
            params = {'limit': limit, 'offset': 0}

            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            games = data.get('games', [])

            # Convert to standardized format
            matches = []
            for game in games:
                match_data = self._extract_match_data(game)
                if match_data:
                    matches.append(match_data)

            logger.info(f"[Leetify] Found {len(matches)} matches for {steam_id}")
            return matches

        except Exception as e:
            logger.error(f"[Leetify] Failed to fetch matches: {e}")
            return []

    async def get_match_details(self, match_id: str, steam_id: str) -> Optional[MatchDetails]:
        """Get detailed match information from Leetify API"""
        if not self._auth_token:
            if not await self.authenticate(steam_id):
                logger.error("[Leetify] Authentication failed")
                return None

        try:
            url = f"{self.base_url}/api/games/{match_id}"
            headers = {
                'Authorization': f'Bearer {self._auth_token}',
                'Content-Type': 'application/json'
            }

            response = await self.client.get(url, headers=headers)

            if response.status_code == 404:
                logger.warning(f"[Leetify] Match {match_id} not found")
                return None

            response.raise_for_status()
            game_data = response.json()

            # Extract match metadata
            match_data = self._extract_match_data(game_data)
            if not match_data:
                return None

            # Extract player performances
            players = []
            for player_data in game_data.get("players", []):
                player_perf = self._extract_player_performance(player_data)
                if player_perf:
                    players.append(player_perf)

            return MatchDetails(match_data=match_data, players=players)

        except Exception as e:
            logger.error(f"[Leetify] Failed to fetch match details for {match_id}: {e}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def _extract_match_data(self, game_data: Dict[str, Any]) -> Optional[MatchData]:
        """Convert Leetify game data to standardized MatchData"""
        try:
            # Convert timestamps from milliseconds
            start_time = None
            end_time = None

            if game_data.get('startTime'):
                start_time = datetime.fromtimestamp(game_data['startTime'] / 1000)
            if game_data.get('endTime'):
                end_time = datetime.fromtimestamp(game_data['endTime'] / 1000)

            return MatchData(
                match_id=game_data.get('matchId'),
                map_name=game_data.get('map', 'Unknown'),
                started_at=start_time,
                finished_at=end_time,
                score_team1=game_data.get('teamAScore', 0),
                score_team2=game_data.get('teamBScore', 0),
                game_type=game_data.get('gameType', 'competitive'),
                demo_url=game_data.get('demoUrl'),
                raw_data=game_data
            )
        except Exception as e:
            logger.error(f"[Leetify] Failed to extract match data: {e}")
            return None

    def _extract_player_performance(self, player_data: Dict[str, Any]) -> Optional[PlayerPerformance]:
        """Convert Leetify player data to standardized PlayerPerformance"""
        try:
            # Convert team string to integer (A -> 1, B -> 2)
            team = player_data.get("team")
            team_int = 1 if team == "A" else 2 if team == "B" else 1

            return PlayerPerformance(
                steam_id=player_data.get("steamId"),
                player_name=player_data.get("name", "Unknown"),
                team=team_int,
                kills=player_data.get("kills", 0),
                deaths=player_data.get("deaths", 0),
                assists=player_data.get("assists", 0),
                adr=player_data.get("adr", 0.0),
                rating=player_data.get("rating", 0.0),
                headshots=player_data.get("headshots", 0),
                mvps=player_data.get("mvps", 0)
            )
        except Exception as e:
            logger.error(f"[Leetify] Failed to extract player performance: {e}")
            return None


# Factory function
def get_leetify_adapter() -> LeetifyAdapter:
    """Get a new Leetify adapter instance"""
    return LeetifyAdapter()