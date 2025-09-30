"""
Match data providers package
"""

from .base import MatchDataProvider, MatchData, PlayerPerformance, MatchDetails
from .leetify_adapter import LeetifyAdapter, get_leetify_adapter
from .steam_adapter import SteamAdapter, get_steam_adapter
from .factory import (
    MatchProviderFactory,
    ProviderType,
    get_match_provider,
    get_leetify_provider,
    get_steam_provider
)

__all__ = [
    # Base classes
    'MatchDataProvider',
    'MatchData',
    'PlayerPerformance',
    'MatchDetails',
    # Adapters
    'LeetifyAdapter',
    'SteamAdapter',
    # Factory
    'MatchProviderFactory',
    'ProviderType',
    # Convenience functions
    'get_match_provider',
    'get_leetify_adapter',
    'get_leetify_provider',
    'get_steam_adapter',
    'get_steam_provider',
]