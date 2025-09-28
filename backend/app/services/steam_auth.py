import re
import urllib.parse
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings


class SteamOpenIDAuth:
    """Steam OpenID authentication handler"""

    def __init__(self):
        self.openid_url = settings.STEAM_OPENID_URL
        self.realm = settings.FRONTEND_URL
        self.return_to = f"{settings.BACKEND_URL}/api/v1/auth/steam/callback"

    def get_auth_url(self) -> str:
        """Generate Steam OpenID authentication URL"""
        params = {
            'openid.ns': 'http://specs.openid.net/auth/2.0',
            'openid.mode': 'checkid_setup',
            'openid.return_to': self.return_to,
            'openid.realm': self.realm,
            'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
            'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
        }

        return f"{self.openid_url}/login?" + urllib.parse.urlencode(params)

    async def verify_auth_response(self, response_params: Dict[str, str]) -> Optional[str]:
        """
        Verify Steam OpenID authentication response
        Returns Steam ID if successful, None if failed
        """
        # Check if response contains required OpenID parameters
        if 'openid.mode' not in response_params:
            return None

        if response_params['openid.mode'] != 'id_res':
            return None

        # Prepare verification request
        verify_params = dict(response_params)
        verify_params['openid.mode'] = 'check_authentication'

        # Send verification request to Steam
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.openid_url}/login",
                    data=verify_params,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                response.raise_for_status()

                # Check if Steam confirms the authentication
                if 'is_valid:true' in response.text:
                    # Extract Steam ID from the claimed_id
                    steam_id = self.extract_steam_id(response_params.get('openid.claimed_id', ''))
                    return steam_id

            except httpx.RequestError:
                pass

        return None

    def extract_steam_id(self, claimed_id: str) -> Optional[str]:
        """Extract Steam ID from OpenID claimed_id URL"""
        # Steam OpenID claimed_id format: https://steamcommunity.com/openid/id/{STEAM_ID}
        match = re.search(r'/openid/id/(\d+)$', claimed_id)
        if match:
            return match.group(1)
        return None

    def validate_return_url(self, return_to: str) -> bool:
        """Validate that the return_to URL matches our expected URL"""
        return return_to == self.return_to


# Global instance
steam_auth = SteamOpenIDAuth()