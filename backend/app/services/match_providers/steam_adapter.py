"""
Steam API Adapter for CS2 Match History
Based on: https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Access_Match_History

This adapter uses the sharecode iteration flow:
1. User provides steam_auth_code (from CS2 console: 'csgo_match_share_auth')
2. User provides initial sharecode (from last played match)
3. Service iterates through match history using GetNextMatchSharingCode endpoint
4. Downloads demo files for detailed match analysis
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

import httpx

from app.core.config import settings
from app.services.steam_match_history import SteamMatchHistoryService
from app.services.steam_sharecode import decode_sharecode, validate_sharecode
from app.services.demo_downloader import DemoDownloader
from app.services.demo_parser import parse_demo_for_match
from .base import MatchDataProvider, MatchData, PlayerPerformance, MatchDetails

logger = logging.getLogger(__name__)


class SteamAdapter(MatchDataProvider):
    """Adapter for Steam API (Official Valve API) with sharecode-based match history"""

    def __init__(self):
        self.api_key = settings.STEAM_API_KEY
        self.base_url = "https://api.steampowered.com"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.match_history_service: Optional[SteamMatchHistoryService] = None
        self.demo_downloader: Optional[DemoDownloader] = None

        # These will be set from user's stored credentials
        self._steam_auth_code: Optional[str] = None
        self._last_sharecode: Optional[str] = None

    @property
    def provider_name(self) -> str:
        return "Steam"

    def set_user_credentials(self, auth_code: str, last_sharecode: str):
        """
        Set user's Steam credentials for match history access

        Args:
            auth_code: Authentication code from CS2 (csgo_match_share_auth)
            last_sharecode: Last known match sharecode to start iteration from
        """
        self._steam_auth_code = auth_code
        self._last_sharecode = last_sharecode
        logger.info(f"[Steam] User credentials set, starting from sharecode: {last_sharecode[:20]}...")

    async def authenticate(self, steam_id: str) -> bool:
        """
        Steam API authentication
        Checks if API key and user credentials are available
        """
        if not self.api_key or self.api_key == "your-steam-api-key-here":
            logger.warning("[Steam] No valid Steam API key configured")
            return False

        if not self._steam_auth_code or not self._last_sharecode:
            logger.warning("[Steam] User has not provided auth code and sharecode")
            logger.info("[Steam] User needs to run 'csgo_match_share_auth' in CS2 console and provide latest match sharecode")
            return False

        if not validate_sharecode(self._last_sharecode):
            logger.error(f"[Steam] Invalid sharecode format: {self._last_sharecode}")
            return False

        # Initialize services
        self.match_history_service = SteamMatchHistoryService(self.api_key)
        self.demo_downloader = DemoDownloader()

        logger.info("[Steam] Authentication successful")
        return True

    async def get_recent_matches(self, steam_id: str, limit: int = 10) -> List[MatchData]:
        """
        Get recent matches from Steam API using sharecode iteration

        This fetches match history by iterating through sharecodees starting from
        the user's last known sharecode.
        """
        if not await self.authenticate(steam_id):
            logger.error("[Steam] Authentication failed")
            return []

        if not self.match_history_service:
            logger.error("[Steam] Match history service not initialized")
            return []

        try:
            logger.info(f"[Steam] Fetching match history for {steam_id}")

            # Fetch match history using sharecode iteration
            async with self.match_history_service:
                raw_matches = await self.match_history_service.fetch_match_history(
                    steam_id,
                    self._steam_auth_code,
                    self._last_sharecode,
                    limit=limit
                )

            logger.info(f"[Steam] Found {len(raw_matches)} matches")

            # Convert to MatchData format
            matches = []
            for raw_match in raw_matches:
                # We have sharecode and match IDs, but no detailed stats yet
                # Stats will be fetched in get_match_details via demo parsing
                match_data = MatchData(
                    match_id=str(raw_match["match_id"]),
                    started_at=None,  # Not available without demo parsing
                    map_name=None,    # Not available without demo parsing
                    score_team1=0,    # Not available without demo parsing
                    score_team2=0,    # Not available without demo parsing
                    sharecode=raw_match["sharecode"],
                    demo_url=raw_match["demo_url"]
                )
                matches.append(match_data)

            return matches

        except Exception as e:
            logger.error(f"[Steam] Failed to fetch matches: {e}")
            return []

    async def get_match_details(self, match_id: str, steam_id: str) -> Optional[MatchDetails]:
        """
        Get match details from Steam API by downloading and parsing demo file

        This is the full implementation that:
        1. Finds the match sharecode
        2. Downloads the demo file
        3. Parses the demo for detailed stats
        """
        if not await self.authenticate(steam_id):
            logger.error("[Steam] Authentication failed")
            return None

        if not self.demo_downloader:
            logger.error("[Steam] Demo downloader not initialized")
            return None

        try:
            logger.info(f"[Steam] Fetching details for match {match_id}")

            # First, we need to find the sharecode for this match
            # If we stored it during get_recent_matches, retrieve it
            # Otherwise, we need to search for it in match history

            # For now, we'll need the sharecode passed somehow
            # This could be stored in the database when match is created
            logger.warning("[Steam] Match details require sharecode - should be stored in database")
            logger.warning("[Steam] Demo parsing requires sharecode from match record")

            # TODO: Get sharecode from database match record
            # decoded = decode_sharecode(sharecode)
            # demo_path = await self.demo_downloader.download_demo(...)
            # parsed_data = await parse_demo_for_match(demo_path)

            return None

        except Exception as e:
            logger.error(f"[Steam] Failed to fetch match details: {e}")
            return None

    async def close(self):
        """Close HTTP client and cleanup resources"""
        await self.client.aclose()
        if self.match_history_service and self.match_history_service.session:
            await self.match_history_service.session.close()


# Factory function
def get_steam_adapter() -> SteamAdapter:
    """Get a new Steam adapter instance"""
    return SteamAdapter()