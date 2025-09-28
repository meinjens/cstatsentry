#!/usr/bin/env python3
"""
Test match sync integration without Celery
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.crud.user import create_user, get_user_by_id, get_user_by_steam_id
from app.crud.match import get_user_matches
from app.services.leetify_api import get_leetify_api_client, LeetifyDataExtractor
from app.crud.match import create_match, get_match_by_id, create_match_player
from app.crud.player import get_player_by_steam_id, create_player


async def process_match_players_async(db, match_details: dict, match_id: str, user_steam_id: str):
    """Process and create player records for a match - copied from tasks"""
    try:
        # Extract players from match details
        players = match_details.get("players", [])

        for player_data in players:
            steam_id = player_data.get("steamId")
            if not steam_id:
                continue

            # Extract player performance data
            performance_data = LeetifyDataExtractor.extract_player_performance(player_data, match_id)

            # Check if player exists in our database
            existing_player = get_player_by_steam_id(db, steam_id)

            if not existing_player:
                # Create new player record
                player_record_data = {
                    "steam_id": steam_id,
                    "current_name": player_data.get("name", "Unknown"),
                    "profile_updated": None,
                    "stats_updated": None
                }
                create_player(db, player_record_data)
                print(f"   Created new player: {steam_id}")

            # Create match player record
            match_player_data = {
                "match_id": match_id,
                "steam_id": steam_id,
                "team": performance_data.get("team", 1),
                "kills": performance_data.get("kills", 0),
                "deaths": performance_data.get("deaths", 0),
                "assists": performance_data.get("assists", 0),
                "headshot_percentage": performance_data.get("headshots", 0) / max(performance_data.get("kills", 1), 1) * 100 if performance_data.get("headshots") else 0
            }

            create_match_player(db, match_player_data)

    except Exception as e:
        print(f"Error processing players for match {match_id}: {e}")
        raise


async def simulate_match_sync(user_id: int):
    """Simulate the match sync task"""
    db = SessionLocal()
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            print(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}

        if not user.sync_enabled:
            print(f"Sync disabled for user {user_id}")
            return {"status": "skipped", "message": "Sync disabled"}

        print(f"Fetching matches for user {user_id} (Steam ID: {user.steam_id})")

        # Fetch matches from Leetify API
        matches_found = 0
        new_matches = 0

        async with get_leetify_api_client() as leetify_api:
            try:
                # Get recent games from Leetify API
                games = await leetify_api.get_recent_games(user.steam_id, limit=10)
                matches_found = len(games)
                print(f"Found {matches_found} matches for user {user_id}")

                for game in games:
                    # Extract match data
                    match_data = LeetifyDataExtractor.extract_match_data(game)
                    match_id = match_data["match_id"]

                    if not match_id:
                        print(f"Skipping match with missing ID for user {user_id}")
                        continue

                    # Check if match already exists
                    existing_match = get_match_by_id(db, match_id)
                    if existing_match:
                        print(f"Match {match_id} already exists, skipping")
                        continue

                    # Get detailed match information
                    match_details = await leetify_api.get_game_details(match_id, user.steam_id)
                    if not match_details:
                        print(f"Could not get details for match {match_id}")
                        continue

                    # Create match record
                    try:
                        # Remove fields that don't exist in the Match model
                        db_match_data = {
                            "match_id": match_id,
                            "user_id": user_id,
                            "match_date": match_data.get("started_at") or datetime.utcnow(),
                            "map": match_data.get("map_name"),
                            "score_team1": match_data.get("score_team1"),
                            "score_team2": match_data.get("score_team2"),
                            "leetify_match_id": match_id,
                            "processed": False
                        }

                        created_match = create_match(db, db_match_data)
                        new_matches += 1
                        print(f"Created match {match_id} for user {user_id}")

                        # Process players in this match
                        await process_match_players_async(db, match_details, match_id, user.steam_id)

                    except Exception as e:
                        print(f"Failed to create match {match_id}: {e}")
                        db.rollback()

            except Exception as e:
                print(f"Failed to fetch matches from Leetify API: {e}")
                db.rollback()

        # Update last_sync timestamp
        user.last_sync = datetime.utcnow()
        db.commit()

        return {
            "status": "completed",
            "user_id": user_id,
            "matches_found": matches_found,
            "new_matches": new_matches
        }

    except Exception as e:
        print(f"Error fetching matches for user {user_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def test_match_sync():
    """Test the complete match sync workflow"""
    print("🧪 Testing Match Sync Workflow")
    print("=" * 50)

    db = SessionLocal()
    try:
        # Create or get test user
        test_steam_id = "76561198123456789"
        user = get_user_by_steam_id(db, test_steam_id)

        if not user:
            test_user_data = {
                "steam_id": test_steam_id,
                "steam_name": "TestUser",
                "avatar_url": "https://example.com/avatar.jpg",
                "sync_enabled": True
            }
            user = create_user(db, test_user_data)
            print(f"✅ Test user created with ID: {user.user_id}")
        else:
            print(f"✅ Using existing test user with ID: {user.user_id}")
            # Ensure sync is enabled
            if not user.sync_enabled:
                user.sync_enabled = True
                db.commit()

        # Check initial matches
        initial_matches = get_user_matches(db, user.user_id)
        print(f"📊 Initial matches: {len(initial_matches)}")

        # Run match sync simulation
        print(f"\n🔄 Running match sync simulation...")
        result = await simulate_match_sync(user.user_id)
        print(f"✅ Match sync result: {result}")

        # Check final matches
        final_matches = get_user_matches(db, user.user_id)
        print(f"📊 Final matches: {len(final_matches)}")

        for match in final_matches:
            print(f"   - {match.match_id}: {match.map} ({match.score_team1}-{match.score_team2})")

        print(f"\n✅ Successfully added {len(final_matches) - len(initial_matches)} new matches")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    print("\n" + "=" * 50)
    print("🎉 Match sync test completed!")


if __name__ == "__main__":
    asyncio.run(test_match_sync())