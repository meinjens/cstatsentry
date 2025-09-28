import httpx
import asyncio
from typing import Dict, List, Optional, Any
from app.core.config import settings


class SteamAPIClient:
    def __init__(self):
        self.api_key = settings.STEAM_API_KEY
        self.base_url = settings.STEAM_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_player_summaries(self, steam_ids: List[str]) -> Dict[str, Any]:
        """Get player summaries for multiple Steam IDs"""
        # Steam API allows up to 100 steam IDs per request
        if len(steam_ids) > 100:
            raise ValueError("Maximum 100 Steam IDs per request")

        steam_ids_str = ",".join(steam_ids)
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v0002/"

        params = {
            "key": self.api_key,
            "steamids": steam_ids_str
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_player_bans(self, steam_ids: List[str]) -> Dict[str, Any]:
        """Get VAC and community ban status for players"""
        if len(steam_ids) > 100:
            raise ValueError("Maximum 100 Steam IDs per request")

        steam_ids_str = ",".join(steam_ids)
        url = f"{self.base_url}/ISteamUser/GetPlayerBans/v1/"

        params = {
            "key": self.api_key,
            "steamids": steam_ids_str
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_owned_games(self, steam_id: str) -> Dict[str, Any]:
        """Get owned games for a player (requires public profile)"""
        url = f"{self.base_url}/IPlayerService/GetOwnedGames/v0001/"

        params = {
            "key": self.api_key,
            "steamid": steam_id,
            "format": "json",
            "include_appinfo": "true",
            "include_played_free_games": "true"
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_user_stats_for_game(self, steam_id: str, app_id: int = 730) -> Dict[str, Any]:
        """Get user stats for CS2 (app_id 730)"""
        url = f"{self.base_url}/ISteamUserStats/GetUserStatsForGame/v0002/"

        params = {
            "appid": app_id,
            "key": self.api_key,
            "steamid": steam_id
        }

        response = await self.client.get(url, params=params)
        if response.status_code == 403:
            # Profile is private or stats not available
            return {"error": "private_profile"}

        response.raise_for_status()
        return response.json()

    async def get_recently_played_games(self, steam_id: str) -> Dict[str, Any]:
        """Get recently played games for a player"""
        url = f"{self.base_url}/IPlayerService/GetRecentlyPlayedGames/v0001/"

        params = {
            "key": self.api_key,
            "steamid": steam_id,
            "format": "json"
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class SteamDataExtractor:
    """Helper class to extract and normalize data from Steam API responses"""

    @staticmethod
    def extract_player_data(player_summary: Dict) -> Dict[str, Any]:
        """Extract relevant player data from Steam API response"""
        from datetime import datetime

        # Convert timestamps to datetime objects
        account_created = player_summary.get("timecreated")
        if account_created:
            account_created = datetime.fromtimestamp(account_created)

        last_logoff = player_summary.get("lastlogoff")
        if last_logoff:
            last_logoff = datetime.fromtimestamp(last_logoff)

        return {
            "steam_id": player_summary.get("steamid"),
            "current_name": player_summary.get("personaname"),
            "avatar_url": player_summary.get("avatarfull"),
            "profile_url": player_summary.get("profileurl"),
            "account_created": account_created,
            "last_logoff": last_logoff,
            "profile_state": player_summary.get("profilestate"),
            "visibility_state": player_summary.get("communityvisibilitystate"),
            "country_code": player_summary.get("loccountrycode")
        }

    @staticmethod
    def extract_ban_data(ban_info: Dict) -> Dict[str, Any]:
        """Extract ban information from Steam API response"""
        return {
            "steam_id": ban_info.get("SteamId"),
            "community_banned": ban_info.get("CommunityBanned", False),
            "vac_banned": ban_info.get("VACBanned", False),
            "number_of_vac_bans": ban_info.get("NumberOfVACBans", 0),
            "days_since_last_ban": ban_info.get("DaysSinceLastBan", 0),
            "number_of_game_bans": ban_info.get("NumberOfGameBans", 0),
            "economy_ban": ban_info.get("EconomyBan", "none")
        }

    @staticmethod
    def extract_cs2_hours(owned_games: Dict) -> int:
        """Extract CS2 playtime from owned games"""
        if "response" not in owned_games or "games" not in owned_games["response"]:
            return 0

        for game in owned_games["response"]["games"]:
            # CS2 app_id is 730
            if game.get("appid") == 730:
                return game.get("playtime_forever", 0) // 60  # Convert minutes to hours

        return 0

    @staticmethod
    def extract_total_games(owned_games: Dict) -> int:
        """Extract total number of owned games"""
        if "response" not in owned_games:
            return 0

        return owned_games["response"].get("game_count", 0)


# Factory function instead of global instance
def get_steam_api_client() -> SteamAPIClient:
    """Get a new Steam API client instance"""
    return SteamAPIClient()


# Backward compatibility for tests - deprecated, use get_steam_api_client() instead
steam_api = SteamAPIClient()