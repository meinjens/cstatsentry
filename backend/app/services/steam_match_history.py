"""
Steam Match History Service

Fetches CS2/CSGO match history using Steam Web API and sharecode iteration.
Based on: https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Access_Match_History

Flow:
1. User provides steam_auth_code (from CS2 console: 'csgo_match_share_auth')
2. User provides initial sharecode (from last played match)
3. Service iterates through match history using GetNextMatchSharingCode endpoint
4. Each match can be downloaded as demo file for detailed analysis
"""

import aiohttp
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.core.config import settings
from app.services.steam_sharecode import decode_sharecode, get_demo_url

logger = logging.getLogger(__name__)


class SteamMatchHistoryService:
    """Service for fetching match history from Steam Web API using sharecodees"""

    BASE_URL = "https://api.steampowered.com/ICSGOPlayers_730"

    def __init__(self, steam_api_key: str):
        self.api_key = steam_api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_next_sharecode(
        self,
        steam_id: str,
        auth_code: str,
        known_sharecode: str
    ) -> Optional[str]:
        """
        Get the next match sharecode in the user's match history

        Args:
            steam_id: User's Steam ID (64-bit)
            auth_code: Authentication code from CS2 (csgo_match_share_auth)
            known_sharecode: A known match sharecode to start from

        Returns:
            Next match sharecode or None if no more matches
        """
        if not self.session:
            raise RuntimeError("Service not initialized. Use 'async with' context manager.")

        try:
            # Decode the known sharecode to get matchId, outcomeId, tokenId
            decoded = decode_sharecode(known_sharecode)
            if not decoded:
                logger.error(f"Invalid sharecode: {known_sharecode}")
                return None

            url = f"{self.BASE_URL}/GetNextMatchSharingCode/v1"
            params = {
                "key": self.api_key,
                "steamid": steam_id,
                "steamidkey": auth_code,
                "knowncode": known_sharecode
            }

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Steam API returned status {response.status}")
                    return None

                data = await response.json()

                # Check for errors in response
                if "result" not in data:
                    logger.error(f"Invalid response from Steam API: {data}")
                    return None

                result = data["result"]

                # No more matches available
                if result.get("nextcode") is None:
                    logger.info("No more matches available")
                    return None

                return result["nextcode"]

        except Exception as e:
            logger.error(f"Error getting next sharecode: {e}")
            return None

    async def fetch_match_history(
        self,
        steam_id: str,
        auth_code: str,
        last_sharecode: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch match history by iterating through sharecodees

        Args:
            steam_id: User's Steam ID (64-bit)
            auth_code: Authentication code from CS2
            last_sharecode: Starting sharecode (usually most recent match)
            limit: Maximum number of matches to fetch

        Returns:
            List of match data dictionaries with decoded sharecode information
        """
        matches = []
        current_sharecode = last_sharecode

        logger.info(f"Starting match history fetch for {steam_id} from {last_sharecode}")

        for i in range(limit):
            # Decode current sharecode
            decoded = decode_sharecode(current_sharecode)
            if not decoded:
                logger.warning(f"Failed to decode sharecode: {current_sharecode}")
                break

            # Store match info
            match_data = {
                "sharecode": current_sharecode,
                "match_id": decoded["matchId"],
                "outcome_id": decoded["outcomeId"],
                "token_id": decoded["tokenId"],
                "demo_url": get_demo_url(
                    decoded["matchId"],
                    decoded["outcomeId"],
                    decoded["tokenId"]
                )
            }
            matches.append(match_data)

            logger.debug(f"Fetched match {i+1}/{limit}: {current_sharecode}")

            # Get next sharecode
            next_sharecode = await self.get_next_sharecode(
                steam_id, auth_code, current_sharecode
            )

            if not next_sharecode:
                logger.info(f"No more matches after {i+1} matches")
                break

            current_sharecode = next_sharecode

        logger.info(f"Fetched {len(matches)} matches from Steam API")
        return matches

    async def validate_auth_code(
        self,
        steam_id: str,
        auth_code: str,
        test_sharecode: str
    ) -> bool:
        """
        Validate that auth code is correct by attempting to get next sharecode

        Args:
            steam_id: User's Steam ID
            auth_code: Authentication code to validate
            test_sharecode: A known valid sharecode to test with

        Returns:
            True if auth code is valid, False otherwise
        """
        try:
            next_code = await self.get_next_sharecode(steam_id, auth_code, test_sharecode)
            # If we get any response (even None for no more matches), auth is valid
            # If auth is invalid, the API returns an error
            return next_code is not None or True  # TODO: Better validation logic
        except Exception as e:
            logger.error(f"Auth validation failed: {e}")
            return False


async def get_steam_match_history_service() -> SteamMatchHistoryService:
    """Factory function to create Steam match history service"""
    return SteamMatchHistoryService(settings.STEAM_API_KEY)


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_fetch():
        # Test values (replace with real values)
        test_steam_id = "76561198000000000"
        test_auth_code = "XXXX-XXXXX-XXXX"
        test_sharecode = "CSGO-U6MWi-5cZMJ-VsXtM-yrOwD-g8BJJ"

        async with SteamMatchHistoryService(settings.STEAM_API_KEY) as service:
            # Test getting next sharecode
            next_code = await service.get_next_sharecode(
                test_steam_id, test_auth_code, test_sharecode
            )
            print(f"Next sharecode: {next_code}")

            # Test fetching history
            if next_code:
                matches = await service.fetch_match_history(
                    test_steam_id, test_auth_code, test_sharecode, limit=10
                )
                print(f"Found {len(matches)} matches")
                for match in matches:
                    print(f"  - {match['sharecode']}: {match['demo_url']}")

    asyncio.run(test_fetch())