import logging
from typing import Dict, List, Optional, Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LeetifyAPIClient:
    def __init__(self):
        self.api_key = settings.LEETIFY_API_KEY
        self.base_url = getattr(settings, 'LEETIFY_API_URL', 'http://localhost:5001')  # Default to mock
        self.client = httpx.AsyncClient(timeout=30.0)

    async def authenticate(self, steam_id: str) -> str:
        """Get authentication token for Leetify API"""
        url = f"{self.base_url}/api/auth/token"

        try:
            response = await self.client.post(
                url,
                json={"steam_id": steam_id},
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()

            data = response.json()
            return data.get('access_token')

        except Exception as e:
            logger.error(f"Failed to authenticate with Leetify API: {e}")
            raise

    async def get_recent_games(self, steam_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent games for a player"""
        try:
            # Get auth token
            token = await self.authenticate(steam_id)
            if not token:
                raise Exception("Failed to get authentication token")

            # Fetch games
            url = f"{self.base_url}/api/profile/{steam_id}/games"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            params = {
                'limit': limit,
                'offset': 0
            }

            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('games', [])

        except Exception as e:
            logger.error(f"Failed to fetch games for {steam_id}: {e}")
            raise

    async def get_game_details(self, match_id: str, steam_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific match"""
        try:
            # Get auth token
            token = await self.authenticate(steam_id)
            if not token:
                raise Exception("Failed to get authentication token")

            # Fetch match details
            url = f"{self.base_url}/api/games/{match_id}"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            response = await self.client.get(url, headers=headers)

            if response.status_code == 404:
                logger.warning(f"Match {match_id} not found")
                return None

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to fetch match details for {match_id}: {e}")
            raise

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class LeetifyDataExtractor:
    """Helper class to extract and normalize data from Leetify API responses"""

    @staticmethod
    def extract_match_data(match_data: Dict) -> Dict[str, Any]:
        """Extract relevant match data from Leetify API response"""
        from datetime import datetime

        # Convert timestamps from milliseconds to datetime objects
        start_time = None
        end_time = None

        if match_data.get('startTime'):
            start_time = datetime.fromtimestamp(match_data['startTime'] / 1000)
        if match_data.get('endTime'):
            end_time = datetime.fromtimestamp(match_data['endTime'] / 1000)

        return {
            "match_id": match_data.get("matchId"),
            "game_type": match_data.get("gameType"),
            "map_name": match_data.get("map"),
            "started_at": start_time,
            "finished_at": end_time,
            "rounds": match_data.get("rounds"),
            "score_team1": match_data.get("teamAScore"),
            "score_team2": match_data.get("teamBScore"),
            "result": match_data.get("result"),
            "demo_url": match_data.get("demoUrl"),  # May not be available in mock
        }

    @staticmethod
    def extract_player_performance(player_data: Dict, match_id: str) -> Dict[str, Any]:
        """Extract player performance data from match"""
        # Convert team string to integer (A -> 1, B -> 2)
        team = player_data.get("team")
        if team == "A":
            team_int = 1
        elif team == "B":
            team_int = 2
        else:
            team_int = 1  # Default to team 1

        return {
            "match_id": match_id,
            "steam_id": player_data.get("steamId"),
            "player_name": player_data.get("name"),
            "team": team_int,
            "kills": player_data.get("kills", 0),
            "deaths": player_data.get("deaths", 0),
            "assists": player_data.get("assists", 0),
            "adr": player_data.get("adr", 0.0),
            "rating": player_data.get("rating", 0.0),
            "headshots": player_data.get("headshots", 0),
            "mvps": player_data.get("mvps", 0)
        }

    @staticmethod
    def extract_teammates(match_data: Dict, user_steam_id: str) -> List[str]:
        """Extract teammate Steam IDs from match data"""
        user_team = None
        teammates = []

        # Find user's team
        for player in match_data.get("players", []):
            if player.get("steamId") == user_steam_id:
                user_team = player.get("team")
                break

        if not user_team:
            return teammates

        # Get all teammates (same team, different steam_id)
        for player in match_data.get("players", []):
            if (player.get("team") == user_team and
                player.get("steamId") != user_steam_id):
                teammates.append(player.get("steamId"))

        return teammates


# Factory function instead of global instance
def get_leetify_api_client() -> LeetifyAPIClient:
    """Get a new Leetify API client instance"""
    return LeetifyAPIClient()


# Backward compatibility for tests - deprecated, use get_leetify_api_client() instead
leetify_api = LeetifyAPIClient()