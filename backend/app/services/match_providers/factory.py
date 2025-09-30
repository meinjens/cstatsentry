"""
Match Data Provider Factory

Selects and creates the appropriate match data provider based on configuration
"""

import logging
from typing import Optional, List
from enum import Enum

from app.core.config import settings
from .base import MatchDataProvider
from .leetify_adapter import LeetifyAdapter
from .steam_adapter import SteamAdapter

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Available provider types"""
    LEETIFY = "leetify"
    STEAM = "steam"


class MatchProviderFactory:
    """Factory for creating match data providers"""

    @staticmethod
    def create_provider(provider_type: Optional[ProviderType] = None) -> MatchDataProvider:
        """
        Create a match data provider

        Args:
            provider_type: Specific provider to create, or None to use default

        Returns:
            MatchDataProvider instance
        """
        # Get provider type from settings if not specified
        if provider_type is None:
            configured_provider = getattr(settings, 'MATCH_DATA_PROVIDER', 'leetify').lower()
            try:
                provider_type = ProviderType(configured_provider)
            except ValueError:
                logger.warning(f"Unknown provider '{configured_provider}', falling back to Leetify")
                provider_type = ProviderType.LEETIFY

        # Create the appropriate provider
        if provider_type == ProviderType.LEETIFY:
            logger.info("Creating Leetify match data provider")
            return LeetifyAdapter()
        elif provider_type == ProviderType.STEAM:
            logger.info("Creating Steam match data provider")
            return SteamAdapter()
        else:
            logger.warning(f"Unknown provider type {provider_type}, falling back to Leetify")
            return LeetifyAdapter()

    @staticmethod
    def create_all_providers() -> List[MatchDataProvider]:
        """
        Create all available providers
        Useful for trying multiple sources
        """
        return [
            LeetifyAdapter(),
            SteamAdapter()
        ]

    @staticmethod
    def create_with_fallback(primary: ProviderType, fallback: ProviderType) -> List[MatchDataProvider]:
        """
        Create primary and fallback providers
        Returns list in priority order
        """
        return [
            MatchProviderFactory.create_provider(primary),
            MatchProviderFactory.create_provider(fallback)
        ]


# Convenience functions
def get_match_provider() -> MatchDataProvider:
    """Get the default match data provider"""
    return MatchProviderFactory.create_provider()


def get_leetify_provider() -> LeetifyAdapter:
    """Get Leetify provider specifically"""
    return LeetifyAdapter()


def get_steam_provider() -> SteamAdapter:
    """Get Steam provider specifically"""
    return SteamAdapter()