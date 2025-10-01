#!/usr/bin/env python3
"""
Test Leetify API integration with mock server
"""

import asyncio
import sys
import os
import pytest

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.leetify_api import get_leetify_api_client, LeetifyDataExtractor


@pytest.mark.asyncio
async def test_leetify_api():
    """Test Leetify API client with mock server"""
    print("🧪 Testing Leetify API Integration")
    print("=" * 50)

    test_steam_id = "76561198123456789"

    async with get_leetify_api_client() as leetify_api:
        try:
            print(f"📤 1. Testing authentication for Steam ID: {test_steam_id}")
            token = await leetify_api.authenticate(test_steam_id)
            print(f"✅ Authentication successful! Token: {token[:20]}...")

            print(f"\n📊 2. Fetching recent games...")
            games = await leetify_api.get_recent_games(test_steam_id, limit=5)
            print(f"✅ Found {len(games)} games")

            for i, game in enumerate(games):
                print(f"   Game {i+1}: {game.get('matchId', 'Unknown')} - {game.get('map', 'Unknown map')}")

            if games:
                first_match = games[0]
                match_id = first_match.get('matchId')

                print(f"\n📋 3. Testing match details for: {match_id}")
                match_details = await leetify_api.get_game_details(match_id, test_steam_id)

                if match_details:
                    print(f"✅ Match details retrieved successfully!")

                    # Test data extraction
                    print(f"\n🔍 4. Testing data extraction...")
                    extracted_match = LeetifyDataExtractor.extract_match_data(match_details)
                    print(f"   Extracted match ID: {extracted_match.get('match_id')}")
                    print(f"   Map: {extracted_match.get('map_name')}")
                    print(f"   Score: {extracted_match.get('score_team1')}-{extracted_match.get('score_team2')}")

                    players = match_details.get("players", [])
                    print(f"   Players found: {len(players)}")

                    if players:
                        # Test player performance extraction
                        first_player = players[0]
                        performance = LeetifyDataExtractor.extract_player_performance(first_player, match_id)
                        print(f"   Sample player: {performance.get('player_name')} - {performance.get('kills')}/{performance.get('deaths')}/{performance.get('assists')}")

                        # Test teammate extraction
                        teammates = LeetifyDataExtractor.extract_teammates(match_details, test_steam_id)
                        print(f"   Teammates found: {len(teammates)}")

                else:
                    print(f"❌ Could not get match details")
            else:
                print("ℹ️  No games found to test")

        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 50)
    print("🎉 Leetify API test completed!")


if __name__ == "__main__":
    asyncio.run(test_leetify_api())