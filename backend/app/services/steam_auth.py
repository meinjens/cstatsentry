import re
import urllib.parse
from typing import Optional, Dict, Any
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class SteamOpenIDAuth:
    """Steam OpenID authentication handler"""

    def __init__(self):
        self.openid_url = settings.STEAM_OPENID_URL
        self.realm = settings.FRONTEND_URL
        self.return_to = f"{settings.BACKEND_URL}/api/v1/auth/steam/callback"

    def get_auth_url(self) -> str:
        """Generate Steam OpenID authentication URL"""
        logger.info("Generating Steam OpenID authentication URL")
        logger.debug(f"OpenID URL: {self.openid_url}")
        logger.debug(f"Return to: {self.return_to}")
        logger.debug(f"Realm: {self.realm}")

        params = {
            'openid.ns': 'http://specs.openid.net/auth/2.0',
            'openid.mode': 'checkid_setup',
            'openid.return_to': self.return_to,
            'openid.realm': self.realm,
            'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
            'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
        }

        auth_url = f"{self.openid_url}/login?" + urllib.parse.urlencode(params)
        logger.info(f"Generated auth URL: {auth_url}")
        return auth_url

    async def verify_auth_response(self, response_params: Dict[str, str]) -> Optional[str]:
        """
        Verify Steam OpenID authentication response
        Returns Steam ID if successful, None if failed
        """
        logger.info(f"verify_auth_response called with params: {list(response_params.keys())}")
        logger.debug(f"Full response_params: {response_params}")

        # Check if response contains required OpenID parameters
        if 'openid.mode' not in response_params:
            logger.warning("Missing 'openid.mode' in response parameters")
            return None

        mode = response_params['openid.mode']
        logger.info(f"OpenID mode: {mode}")

        if mode != 'id_res':
            logger.warning(f"Invalid OpenID mode: {mode}, expected 'id_res'")
            return None

        # Log the claimed_id for debugging
        claimed_id = response_params.get('openid.claimed_id', '')
        logger.info(f"OpenID claimed_id: {claimed_id}")

        # Prepare verification request
        verify_params = dict(response_params)
        verify_params['openid.mode'] = 'check_authentication'

        logger.info(f"Sending verification request to Steam: {self.openid_url}/login")
        logger.debug(f"Verification params keys: {list(verify_params.keys())}")

        # Send verification request to Steam
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.openid_url}/login",
                    data=verify_params,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )

                logger.info(f"Steam verification response status: {response.status_code}")
                logger.debug(f"Steam verification response text: {response.text}")

                response.raise_for_status()

                # Check if Steam confirms the authentication
                if 'is_valid:true' in response.text:
                    logger.info("Steam confirmed authentication as valid")
                    # Extract Steam ID from the claimed_id
                    steam_id = self.extract_steam_id(claimed_id)
                    logger.info(f"Extracted Steam ID: {steam_id}")
                    return steam_id
                else:
                    logger.warning(f"Steam authentication invalid. Response: {response.text}")

            except httpx.RequestError as e:
                logger.error(f"HTTP request error during Steam verification: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during Steam verification: {e}")

        logger.warning("Steam authentication verification failed")
        return None

    def extract_steam_id(self, claimed_id: str) -> Optional[str]:
        """Extract Steam ID from OpenID claimed_id URL"""
        logger.debug(f"Extracting Steam ID from claimed_id: {claimed_id}")

        # Steam OpenID claimed_id format: https://steamcommunity.com/openid/id/{STEAM_ID}
        match = re.search(r'/openid/id/(\d+)$', claimed_id)
        if match:
            steam_id = match.group(1)
            logger.info(f"Successfully extracted Steam ID: {steam_id}")
            return steam_id
        else:
            logger.error(f"Failed to extract Steam ID from claimed_id: {claimed_id}")
        return None

    def validate_return_url(self, return_to: str) -> bool:
        """Validate that the return_to URL matches our expected URL"""
        return return_to == self.return_to

    async def test_verification(self) -> dict:
        """Test function to verify Steam auth is working with mock server"""
        logger.info("Testing Steam auth verification with mock server")

        # Mock parameters that the Steam mock server would send
        test_params = {
            'openid.mode': 'id_res',
            'openid.claimed_id': 'https://steamcommunity.com/openid/id/76561198123456789',
            'openid.identity': 'https://steamcommunity.com/openid/id/76561198123456789',
            'openid.return_to': self.return_to,
            'openid.response_nonce': '2025-09-28T10:44:31.732492Z1759056271',
            'openid.assoc_handle': 'test_handle_123',
            'openid.signed': 'signed,mode,identity,return_to,response_nonce,assoc_handle',
            'openid.sig': 'test_signature_valid'
        }

        try:
            steam_id = await self.verify_auth_response(test_params)
            return {
                "success": bool(steam_id),
                "steam_id": steam_id,
                "auth_url": self.get_auth_url(),
                "openid_url": self.openid_url,
                "return_to": self.return_to
            }
        except Exception as e:
            logger.error(f"Test verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "auth_url": self.get_auth_url(),
                "openid_url": self.openid_url,
                "return_to": self.return_to
            }


# Global instance
steam_auth = SteamOpenIDAuth()